import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
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

def add_task(title, status="To Do", priority=3, due_date=""):
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

st.title("✅ Smart To-Do List")
st.caption("Polished, simple & recruiter-friendly — built with Streamlit + SQLite.")

init_db()

# Sidebar: Add task
st.sidebar.header("➕ Add New Task")
title = st.sidebar.text_input("Task")
priority = st.sidebar.selectbox("Priority (1 = highest, 5 = lowest)", [1, 2, 3, 4, 5], index=2)
due_date = st.sidebar.date_input("Due Date (optional)", value=None)

if st.sidebar.button("Add Task"):
    if title.strip():
        due_str = due_date.isoformat() if due_date else ""
        add_task(title, "To Do", priority, due_str)
        st.sidebar.success("Task added!")
        st.rerun()  # FIXED: replaced experimental_rerun
    else:
        st.sidebar.warning("Please enter a task title!")

# Main: Kanban board
df = fetch_tasks()
statuses = ["To Do", "In Progress", "Done"]
cols = st.columns(3)

priority_colors = {
    1: "🔴 Urgent",
    2: "🟠 High",
    3: "🟡 Medium",
    4: "🔵 Low",
    5: "🟢 Very Low"
}

for i, status in enumerate(statuses):
    with cols[i]:
        st.subheader(f"{status}")
        tasks = df[df["status"] == status]
        if tasks.empty:
            st.info("No tasks here 👌")
        for _, row in tasks.iterrows():
            with st.container():
                st.markdown(
                    f"""
                    <div style='padding:10px; border-radius:10px; margin-bottom:10px;
                                background: #f9f9f9; border:1px solid #ddd;'>
                        <b>{row['title']}</b><br>
                        Priority: {priority_colors.get(row['priority'], row['priority'])}<br>
                        Due: {row['due_date'] or '—'}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                c1, c2 = st.columns([1, 1])
                with c1:
                    if st.button("➡ Move", key=f"mv{row['id']}"):
                        next_status = (
                            "In Progress" if status == "To Do"
                            else "Done" if status == "In Progress"
                            else "To Do"
                        )
                        update_status(row['id'], next_status)
                        st.rerun()
                with c2:
                    if st.button("🗑 Delete", key=f"del{row['id']}"):
                        delete_task(row['id'])
                        st.rerun()

# Bottom: Progress tracker
st.markdown("---")
total = len(df)
done = len(df[df["status"] == "Done"])
progress = int((done / total) * 100) if total else 0
st.metric("Tasks Done", f"{done}/{total}")
st.progress(progress/100 if total else 0)

if progress == 100 and total > 0:
    st.success("🎉 All tasks completed! Fantastic work!")
elif progress >= 50:
    st.info("🚀 You're more than halfway there!")

