# Move Daily — Fitness Tracker

A Streamlit activity dashboard with SQLite persistence.

## Features
- Manual date, steps, workout minutes, active calories, and notes
- Daily totals and step/workout progress bars
- Weekly step and workout charts, including days with zero activity
- Activity history and guarded delete control
- SQLite database created automatically

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```
On hosted platforms, local database files may be reset during rebuilds; back up your database if the records matter.
