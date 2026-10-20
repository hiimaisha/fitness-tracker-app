import sqlite3
from datetime import date, timedelta
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Fitness Tracker", page_icon="🏃", layout="wide")
DB_PATH = Path(__file__).with_name("fitness.db")

def connect():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    with connect() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day TEXT NOT NULL,
            steps INTEGER NOT NULL DEFAULT 0,
            workout_minutes INTEGER NOT NULL DEFAULT 0,
            calories INTEGER NOT NULL DEFAULT 0,
            note TEXT DEFAULT ''
        )""")
init_db()

def load_data():
    with connect() as con:
        return pd.read_sql_query("SELECT * FROM activity ORDER BY day DESC, id DESC", con)

st.title("🏃 Fitness Tracker")
st.caption("Log your daily movement and see your progress. Your entries are saved in a local SQLite database.")
today = date.today()
with st.sidebar:
    st.header("➕ Log activity")
    log_day = st.date_input("Date", value=today, max_value=today)
    steps = st.number_input("Steps", min_value=0, max_value=200000, value=5000, step=500)
    minutes = st.number_input("Workout minutes", min_value=0, max_value=1440, value=20, step=5)
    calories = st.number_input("Active calories (optional)", min_value=0, max_value=20000, value=0, step=50)
    note = st.text_input("Note", placeholder="e.g. Evening walk")
    if st.button("Save activity", type="primary", use_container_width=True):
        with connect() as con:
            con.execute("INSERT INTO activity(day, steps, workout_minutes, calories, note) VALUES (?, ?, ?, ?, ?)",
                        (log_day.isoformat(), int(steps), int(minutes), int(calories), note.strip()))
        st.success("Activity saved!")
        st.rerun()

df = load_data()
if df.empty:
    st.info("No activity logged yet. Use the form in the sidebar to add your first entry.")
else:
    df["day"] = pd.to_datetime(df["day"]).dt.date
    start_week = today - timedelta(days=today.weekday())
    week = df[df["day"] >= start_week]
    today_df = df[df["day"] == today]
    total_steps = int(today_df["steps"].sum())
    total_minutes = int(today_df["workout_minutes"].sum())
    total_calories = int(today_df["calories"].sum())
    c1, c2, c3 = st.columns(3)
    c1.metric("Today's steps", f"{total_steps:,}", delta=f"{min(100, int(total_steps/10000*100))}% of 10k goal")
    c2.metric("Workout time", f"{total_minutes} min")
    c3.metric("Active calories", f"{total_calories:,}")
    st.subheader("Today's goals")
    g1, g2 = st.columns(2)
    g1.write(f"**Steps: {total_steps:,} / 10,000**")
    g1.progress(min(total_steps / 10000, 1.0))
    g2.write(f"**Workout: {total_minutes} / 30 minutes**")
    g2.progress(min(total_minutes / 30, 1.0))
    st.subheader("Weekly overview")
    if week.empty:
        st.caption("Log an activity this week to see your weekly chart.")
    else:
        daily = week.groupby("day", as_index=False)[["steps", "workout_minutes", "calories"]].sum()
        daily["day"] = daily["day"].astype(str)
        left, right = st.columns(2)
        with left:
            st.markdown("**Steps per day**")
            st.bar_chart(daily.set_index("day")[["steps"]])
        with right:
            st.markdown("**Workout minutes per day**")
            st.bar_chart(daily.set_index("day")[["workout_minutes"]])
        st.write(f"This week: **{int(week['steps'].sum()):,} steps**, **{int(week['workout_minutes'].sum())} workout minutes**.")
    st.subheader("Recent activity")
    display = df.copy()
    display["day"] = display["day"].astype(str)
    st.dataframe(display[["day", "steps", "workout_minutes", "calories", "note"]].rename(columns={
        "day":"Date", "steps":"Steps", "workout_minutes":"Workout (min)", "calories":"Active calories", "note":"Note"
    }), use_container_width=True, hide_index=True)
    with st.expander("Delete an entry"):
        options = {f"#{int(r.id)} · {r.day} · {int(r.steps):,} steps · {r.note}": int(r.id) for r in df.itertuples()}
        chosen = st.selectbox("Select entry", list(options))
        if st.button("Delete selected entry"):
            with connect() as con:
                con.execute("DELETE FROM activity WHERE id = ?", (options[chosen],))
            st.success("Entry deleted.")
            st.rerun()

st.caption("Tip: use the same date for multiple entries if you want to log separate activities. Daily totals are added together.")
