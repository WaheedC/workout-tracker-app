@echo off
:: Navigate to project directory
cd /d "C:\Users\Waheed\Projects\workout-tracker-app"

:: Launch Streamlit in the background without a command console
start "" pythonw -m streamlit run src/interface.py --server.headless true

:: Wait 3 seconds for the Streamlit server to boot, then open the browser
timeout /t 3 /nobreak >nul
start http://localhost:8501