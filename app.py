import sqlite3
from pathlib import Path
from datetime import date, timedelta
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Move Daily | Fitness Tracker",page_icon="🏃",layout="wide")
DB=Path(__file__).with_name("fitness.db")
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}.stApp{background:#f6f8fb}.block-container{max-width:1250px;padding-top:2rem}
.hero{background:linear-gradient(120deg,#064e3b,#047857 60%,#10b981);color:white;border-radius:24px;padding:1.5rem 1.8rem;margin-bottom:1.2rem}.hero h1{font-family:Manrope,sans-serif;color:white;margin:0}.hero p{color:#d1fae5;margin:.35rem 0 0}
div[data-testid="stMetric"]{background:white;border:1px solid #e4e9ef;border-radius:18px;padding:1.1rem}div.stButton>button{border-radius:12px;min-height:2.7rem;font-weight:700}div.stButton>button[kind="primary"]{background:#047857;color:white;border:0}section[data-testid="stSidebar"]{background:#eff8f3}
</style>""",unsafe_allow_html=True)
def connect(): return sqlite3.connect(DB,check_same_thread=False)
with connect() as c:
    c.execute("""CREATE TABLE IF NOT EXISTS activity(id INTEGER PRIMARY KEY AUTOINCREMENT,day TEXT NOT NULL,steps INTEGER NOT NULL,workout_minutes INTEGER NOT NULL,calories INTEGER NOT NULL,note TEXT DEFAULT '')""")
def get_data():
    with connect() as c: return pd.read_sql_query("SELECT * FROM activity ORDER BY day DESC,id DESC",c)
today=date.today()
st.markdown('<div class="hero"><h1>🏃 Move Daily</h1><p>Your activity, your pace. Log movement and build consistency one day at a time.</p></div>',unsafe_allow_html=True)
with st.sidebar:
    st.header("＋ Log an activity")
    with st.form("log_activity",clear_on_submit=True):
        log_date=st.date_input("Activity date",value=today,max_value=today)
        steps=st.number_input("Steps",min_value=0,max_value=200000,value=5000,step=500)
        minutes=st.number_input("Workout duration (minutes)",min_value=0,max_value=1440,value=20,step=5)
        calories=st.number_input("Active calories (optional)",min_value=0,max_value=20000,value=0,step=25)
        note=st.text_input("Activity note",placeholder="e.g. 25-minute evening walk")
        save=st.form_submit_button("Save activity",type="primary",use_container_width=True)
        if save:
            with connect() as c: c.execute("INSERT INTO activity(day,steps,workout_minutes,calories,note) VALUES(?,?,?,?,?)",(log_date.isoformat(),int(steps),int(minutes),int(calories),note.strip()))
            st.success("Activity saved."); st.rerun()
df=get_data()
if df.empty:
    st.info("Your dashboard is ready. Add your first activity using the form in the left sidebar.")
else:
    df["day"]=pd.to_datetime(df["day"]).dt.date
    today_df=df[df.day==today]; week_start=today-timedelta(days=today.weekday())
    week_df=df[(df.day>=week_start)&(df.day<=today)]
    steps_today=int(today_df.steps.sum()); mins_today=int(today_df.workout_minutes.sum()); cals_today=int(today_df.calories.sum())
    a,b,c=st.columns(3)
    a.metric("Steps today",f"{steps_today:,}",f"{min(100,round(steps_today/10000*100))}% of 10,000 goal")
    b.metric("Workout time today",f"{mins_today} min",f"{min(100,round(mins_today/30*100))}% of 30-min goal")
    c.metric("Active calories today",f"{cals_today:,}")
    st.markdown("### Today's progress")
    g1,g2=st.columns(2)
    with g1: st.write(f"**Step goal** — {steps_today:,} / 10,000"); st.progress(min(steps_today/10000,1.0))
    with g2: st.write(f"**Workout goal** — {mins_today} / 30 min"); st.progress(min(mins_today/30,1.0))
    st.markdown("### This week")
    daily=week_df.groupby("day",as_index=False)[["steps","workout_minutes","calories"]].sum()
    all_days=pd.DataFrame({"day":[week_start+timedelta(days=i) for i in range((today-week_start).days+1)]})
    daily=all_days.merge(daily,on="day",how="left").fillna(0); daily["day_label"]=daily.day.apply(lambda d:d.strftime("%a %d"))
    left,right=st.columns(2)
    with left: st.write("**Steps by day**"); st.bar_chart(daily.set_index("day_label")[["steps"]])
    with right: st.write("**Workout minutes by day**"); st.bar_chart(daily.set_index("day_label")[["workout_minutes"]])
    m1,m2,m3=st.columns(3)
    m1.metric("Weekly steps",f"{int(week_df.steps.sum()):,}"); m2.metric("Weekly workout",f"{int(week_df.workout_minutes.sum())} min"); m3.metric("Days with activity",f"{week_df.day.nunique()} / 7")
    st.markdown("### Activity history")
    display=df.copy(); display["day"]=display.day.astype(str)
    st.dataframe(display[["day","steps","workout_minutes","calories","note"]].rename(columns={"day":"Date","steps":"Steps","workout_minutes":"Workout minutes","calories":"Active calories","note":"Note"}),use_container_width=True,hide_index=True)
    with st.expander("Manage entries"):
        labels={f'#{int(r.id)} · {r.day} · {int(r.steps):,} steps · {r.note or "No note"}':int(r.id) for r in df.itertuples()}
        selected=st.selectbox("Select entry to delete",list(labels))
        confirm=st.checkbox("Confirm I want to delete this entry")
        if st.button("Delete selected entry",disabled=not confirm):
            with connect() as c: c.execute("DELETE FROM activity WHERE id=?",(labels[selected],))
            st.success("Entry deleted."); st.rerun()
st.caption("Entries are saved in SQLite. Local database files on hosted platforms may not survive every rebuild; back up your data if needed.")
