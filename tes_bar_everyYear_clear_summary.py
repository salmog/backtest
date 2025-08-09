import backtrader as bt
import pandas as pd
import optuna
import os

class EmaAtrStrategy(bt.Strategy):
    params = dict(
        fast_ema=10,
        slow_ema=30,
        atr_period=14,
        atr_mult=2.0,
        use_atr_filter=False,
        fractional_size=1.0,
    )

    def __init__(self):
        self.fast_ema = bt.ind.EMA(self.data.close, period=self.p.fast_ema)
        self.slow_ema = bt.ind.EMA(self.data.close, period=self.p.slow_ema)
        self.atr = bt.ind.ATR(self.data, period=self.p.atr_period)

    def next(self):
        if not self.position:
            if self.fast_ema[0] > self.slow_ema[0] and self.fast_ema[-1] <= self.slow_ema[-1]:
                if self.p.use_atr_filter:
                    if self.data.close[0] < self.data.close[-1] + self.p.atr_mult * self.atr[0]:
                        return
                size = self.broker.getcash() * self.p.fractional_size / self.data.close[0]
                self.buy(size=size)
        else:
            if self.fast_ema[0] < self.slow_ema[0] and self.fast_ema[-1] >= self.slow_ema[-1]:
                self.close()

def load_data(ticker, timeframe, years_back=None):
    base_path = f"stock_data/{ticker.lower()}"
    tf_map = {"daily": "daily_10y", "weekly": "weekly_10y", "4h": "4h_729d"}
    file_suffix = tf_map.get(timeframe)
    if not file_suffix:
        raise ValueError(f"Unsupported timeframe: {timeframe}")
    file_path = os.path.join(base_path, f"{ticker.lower()}_{file_suffix}.csv")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found: {file_path}")
    df = pd.read_csv(file_path, parse_dates=["Date"])
    df.set_index("Date", inplace=True)
    if years_back:
        if timeframe in ("daily", "weekly"):
            start_date = df.index[-1] - pd.DateOffset(years=years_back)
        else:
            days = int(years_back * 365)
            start_date = df.index[-1] - pd.Timedelta(days=days)
        df = df.loc[start_date:]
    return df

def run_backtest(df, params, start_cash=100000):
    cerebro = bt.Cerebro(stdstats=False)
    cerebro.broker.setcash(start_cash)
    data = bt.feeds.PandasData(dataname=df)
    cerebro.adddata(data)
    cerebro.addstrategy(EmaAtrStrategy, **params)
    try:
        cerebro.run()
        final_value = cerebro.broker.getvalue()
    except Exception as e:
        # print(f"Backtest error: {e}")
        final_value = 0.0
    return final_value

def buy_and_hold_return(df, start_cash=100000):
    try:
        start_price = df['Close'].iloc[0]
        end_price = df['Close'].iloc[-1]
        ret = (end_price / start_price) * start_cash
    except Exception:
        ret = 0.0
    return ret

def objective(trial, df):
    data_len = len(df)
    max_slow = min(150, data_len - 1)
    if max_slow < 10:
        return 0.0
    fast_ema = trial.suggest_int("fast_ema", 5, max(5, max_slow - 10))
    slow_ema = trial.suggest_int("slow_ema", fast_ema + 1, max_slow)
    if slow_ema >= data_len or fast_ema >= slow_ema:
        return 0.0
    atr_period = trial.suggest_int("atr_period", 5, min(30, data_len // 2))
    atr_mult = round(trial.suggest_float("atr_mult", 1.0, 4.0), 2)
    use_atr_filter = trial.suggest_categorical("use_atr_filter", [False, True])
    fractional_size = round(trial.suggest_float("fractional_size", 0.1, 1.0), 2)

    params = dict(
        fast_ema=fast_ema,
        slow_ema=slow_ema,
        atr_period=atr_period,
        atr_mult=atr_mult,
        use_atr_filter=use_atr_filter,
        fractional_size=fractional_size,
    )
    return round(run_backtest(df, params), 2)

def main():
    tickers = ["xlk", "iwm", "qqq", "aapl"]
    timeframes = ["daily", "weekly", "4h"]
    daily_weekly_years = list(range(1, 11))
    four_h_years = [0.5, 1, 1.5, 2]

    results = []

    for ticker in tickers:
        for tf in timeframes:
            periods_to_test = daily_weekly_years if tf in ("daily", "weekly") else four_h_years
            for period in periods_to_test:
                try:
                    df = load_data(ticker, tf, years_back=period)
                    if len(df) < 30:
                        continue
                    buy_hold_val = round(buy_and_hold_return(df), 2)

                    study = optuna.create_study(direction="maximize")
                    study.optimize(lambda trial: objective(trial, df), n_trials=20, show_progress_bar=True)

                    best_params = study.best_params
                    best_val = round(study.best_value, 2)
                    beat_bh = best_val > buy_hold_val

                    results.append({
                        "Ticker": ticker.upper(),
                        "Timeframe": tf,
                        "Period (years)": f"{period:.2f}",
                        "Strategy Value": best_val,
                        "Buy & Hold": buy_hold_val,
                        "Beat Buy & Hold": "YES" if beat_bh else "NO",
                        "Best Params": {k: (round(v, 2) if isinstance(v, float) else v) for k, v in best_params.items()}
                    })
                    print(f"{ticker.upper()} {tf} {period:.2f}y: Strategy ${best_val:.2f} vs BH ${buy_hold_val:.2f} -> {'Beat' if beat_bh else 'Did NOT beat'}")
                except Exception as e:
                    print(f"Error for {ticker} {tf} {period}: {e}")

    print("\nSummary of results:")
    print(f"{'Ticker':6} {'TF':7} {'Period':7} {'Strategy $':11} {'Buy&Hold $':11} {'Beat BH':9} {'Params'}")
    for r in results:
        print(f"{r['Ticker']:6} {r['Timeframe']:7} {r['Period (years)']:7} "
              f"{r['Strategy Value']:11.2f} {r['Buy & Hold']:11.2f} {r['Beat Buy & Hold']:9} {r['Best Params']}")

if __name__ == "__main__":
    main()
