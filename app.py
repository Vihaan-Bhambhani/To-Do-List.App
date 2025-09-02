import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date, timedelta
import uuid

DB_FILE = "tasks.db"

# ---------------- DB Helpers ----------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        title TEXT,
        status TEXT,
        priority INTEGER,
        created_at TEXT,
        due_date TEXT
    )
    """)
    conn.commit()
    conn.close()

def add_task(title, status="To Do", priority=2, due_date=""):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    tid = str(uuid.uuid4())
    created = datetime.utcnow().isoformat()
    c.execute("INSERT INTO tasks VALUES (?,?,?,?,?,?)",
              (tid, title, status, priority, created, due_date))
    conn.commit()
    conn.close()

def update_status(tid, status):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE tasks SET status=? WHERE id=?", (status, tid))
    conn.commit()
    conn.close()

def delete_task(tid):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id=?", (tid,))
    conn.commit()
    conn.close()

def fetch_tasks():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM tasks", conn)
    conn.close()
    return df

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="📝 To-Do List", page_icon="✅", layout="wide")

st.title("📝 To-Do List App")
st.caption("A simple but polished Streamlit app — powered by SQLite.")

init_db()

# Sidebar: Add task
st.sidebar.header("Add Task")
title = st.sidebar.text_input("Task")
priority = st.sidebar.selectbox("Priority", [1, 2, 3], index=1)
due_date = st.sidebar.date_input("Due Date (optional)", value=None)

if st.sidebar.button("Add"):
    if title.strip():
        due_str = due_date.isoformat() if due_date else ""
        add_task(title, "To Do", priority, due_str)
        st.sidebar.success("Task added!")
        st.experimental_rerun()

# Main: Kanban board
df = fetch_tasks()
statuses = ["To Do", "In Progress", "Done"]
cols = st.columns(3)

for i, status in enumerate(statuses):
    with cols[i]:
        st.subheader(f"{status}")
        tasks = df[df["status"] == status]
        for _, row in tasks.iterrows():
            with st.expander(f"{row['title']} (P{row['priority']})"):
                st.write(f"Due: {row['due_date'] or '—'}")
                if st.button("➡ Move", key=f"mv{row['id']}"):
                    next_status = (
                        "In Progress" if status == "To Do"
                        else "Done" if status == "In Progress"
                        else "To Do"
                    )
                    update_status(row['id'], next_status)
                    st.experimental_rerun()
                if st.button("🗑 Delete", key=f"del{row['id']}"):
                    delete_task(row['id'])
                    st.experimental_rerun()

# Bottom: Progress
st.markdown("---")
total = len(df)
done = len(df[df["status"] == "Done"])
progress = int((done / total) * 100) if total else 0
st.metric("Tasks Done", f"{done}/{total}")
st.progress(progress/100 if total else 0)
