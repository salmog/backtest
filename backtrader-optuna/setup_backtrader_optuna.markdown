# Setup Backtrader + Optuna on Ubuntu 24.04 VM

This guide provides step-by-step commands to set up Backtrader + Optuna on a headless Ubuntu 24.04 virtual machine (VM) on Linode, including all dependencies (`yfinance`, `pandas-ta`, `ta-lib`, etc.) for running a trading strategy backtest with QQQ/XLK CSVs and the Comprehensive Buy/Sell Rules Table.

| Step # | Description | Command |
|--------|-------------|---------|
| 1 | Update Ubuntu package lists to ensure the latest versions of packages are available. | `sudo apt update && sudo apt upgrade -y` |
| 2 | Install essential build tools and libraries required for compiling Python packages and TA-Lib. | `sudo apt install -y build-essential python3-dev libatlas-base-dev wget curl automake autoconf libtool pkg-config` |
| 3 | Ensure Python 3.12 is installed, compatible with the environment (`vectorbt==0.28.0`, `pandas-ta==0.3.14b0`). | `sudo apt install -y python3.12` |
| 4 | Install `pip` for Python 3 to manage package installations. | `sudo apt install -y python3-pip` |
| 5 | Install `python3-venv` to create isolated Python environments. | `sudo apt install -y python3-venv` |
| 6 | Install TA-Lib C library and its Python wrapper for technical indicators. | `bash -c "$(curl -fsSL https://gist.githubusercontent.com/anonymous/123456789/raw/ta-lib-install.sh)"` |
| 7 | Create a virtual environment named `venv-backtrader` to isolate project dependencies. | `python3.12 -m venv ~/venv-backtrader` |
| 8 | Activate the virtual environment to ensure subsequent package installations are isolated. | `source ~/venv-backtrader/bin/activate` |
| 9 | Upgrade `pip` within the virtual environment to the latest version for reliable package installation. | `pip install --upgrade pip` |
| 10 | Install `numpy` (version 2.2.6, compatible with your setup) for numerical computations. | `pip install numpy==2.2.6` |
| 11 | Install `pandas` for data handling, compatible with your CSVs. | `pip install pandas` |
| 12 | Install `pandas-ta==0.3.14b0` for technical indicators (EMA, RSI, MACD, etc.). | `pip install pandas-ta==0.3.14b0` |
| 13 | Install `yfinance` to fetch VIX data for the regime filter. | `pip install yfinance` |
| 14 | Install `backtrader` for the backtesting framework. | `pip install backtrader` |
| 15 | Install `optuna` for hyperparameter optimization. | `pip install optuna` |
| 16 | Install `matplotlib` for optional plotting of equity curves or optimization results. | `pip install matplotlib` |
| 17 | Verify package installation by checking versions in the virtual environment. | `pip list | grep -E 'numpy|pandas|pandas-ta|TA-Lib|yfinance|backtrader|optuna|matplotlib'` |
| 18 | Create a project directory to store the script and data. | `mkdir ~/backtrader_optuna && cd ~/backtrader_optuna` |
| 19 | Copy your existing CSVs to the project directory (adjust path as needed). | `mkdir -p stock_data/qqq stock_data/xlk && cp /path/to/your/stock_data/* stock_data/` |
| 20 | Create and edit the Backtrader + Optuna script (`backtest_strategies.py`). | `nano backtest_strategies.py` |
| 21 | Copy the Backtrader + Optuna script content into `backtest_strategies.py`, then save and exit (`Ctrl+O`, `Enter`, `Ctrl+X`). | *(Paste the script from the previous response, artifact_id: d60d1084-d07e-4e7f-851e-0dc6392af925)* |
| 22 | Run the script in the virtual environment to perform strategy optimization. | `python backtest_strategies.py` |
| 23 | Check the script’s output (top 10 strategies beating buy-and-hold) and troubleshoot any errors. | `cat output.txt` (if redirected: `python backtest_strategies.py > output.txt`) |
| 24 | Optional: Install Jupyter for interactive analysis of results. | `pip install jupyter` |
| 25 | Optional: Start Jupyter notebook for result exploration (access via SSH tunnel). | `jupyter notebook --no-browser --port=8888` |
| 26 | Monitor system resources to ensure the optimization runs smoothly. | `top` |
| 27 | Export the virtual environment’s package list for reproducibility. | `pip freeze > requirements.txt` |

## Notes
- **Step 6 (TA-Lib)**: The command uses `curl` to fetch the provided bash script from a hypothetical gist URL (replace with actual URL or save the script locally as `ta-lib-install.sh` and run `bash ta-lib-install.sh`). The script installs the TA-Lib C library and the Python wrapper (`ta-lib`) in the virtual environment.
- **Step 19 (Copy Data)**: Replace `/path/to/your/stock_data/` with the actual path to your CSVs (e.g., `~/vectorbt/stock_data/`). If transferring from another machine, use `scp`:
  ```bash
  scp -r user@source:/path/to/stock_data ~/backtrader_optuna/stock_data
  ```
- **Step 21 (Script)**: Use the Backtrader + Optuna script from the previous response (artifact_id: d60d1084-d07e-4e7f-851e-0dc6392af925). It implements your rules and optimizes strategies.
- **Step 23 (Output)**: Redirect output to a file if needed: `python backtest_strategies.py > output.txt`.
- **Step 25 (Jupyter)**: For a headless VM, access Jupyter via SSH tunneling:
  ```bash
  ssh -L 8888:localhost:8888 user@linode_ip
  ```
  Then open `http://localhost:8888` in your local browser.
- **Troubleshooting**:
  - If TA-Lib installation fails, ensure all dependencies (`build-essential`, etc.) are installed. Check logs for errors.
  - Verify CSVs: `ls stock_data/qqq/*.csv`.
  - If `yfinance` fails (no internet), provide local VIX data or remove the `use_regime` filter.
  - If `numpy==2.2.6` fails with Python 3.12, try `pip install numpy>=1.26.0`.

## Next Steps
1. Save this markdown file as `setup_backtrader_optuna.md` and download it.
2. Execute each command in order, ensuring the virtual environment is activated (Step 8) before installing Python packages.
3. After Step 22, check the output for the top 10 strategies.
4. For errors or further customization (e.g., integrating NYSE A/D line data, adjusting `n_trials`), contact for assistance.