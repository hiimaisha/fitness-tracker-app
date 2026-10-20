# Fitness Tracker

A Streamlit fitness dashboard with manual activity logging and SQLite persistence.

## Features
- Log date, steps, workout minutes, active calories, and notes
- Daily metrics and simple progress bars
- Weekly step and workout charts
- Recent log table and delete-entry control
- SQLite database created automatically

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

The app creates `fitness.db` beside `app.py` on first run. On Streamlit hosting, local files can be reset in some redeploy/rebuild situations; download or back up the database if the data is important.
