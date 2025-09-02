import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import random
from datetime import datetime

# -----------------------
# Database Setup & Helpers
# -----------------------
DB_FILE = "tasks.db"

def get_conn():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT,
            status TEXT,
            priority INTEGER,
            tag TEXT,
            due_date TEXT,
            created_at TEXT,
            completed_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_task(title, priority, tag, due_date):
    conn = get_conn()
    c = conn.cursor()
    # use timestamp as unique ID (avoids int/UUID mismatch)
    task_id = str(datetime.now().timestamp()).replace(".", "")
    c.execute(
        "INSERT INTO tasks (id, title, status, priority, tag, due_date, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (task_id, title, "To Do", priority, tag, due_date, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def update_status(task_id, new_status):
    conn = get_conn()
    c = conn.cursor()
    if new_status == "Done":
        c.execute("UPDATE tasks SET status=?, completed_at=? WHERE id=?", (new_status, datetime.now().isoformat(), task_id))
    else:
        c.execute("UPDATE tasks SET status=? WHERE id=?", (new_status, task_id))
    conn.commit()
    conn.close()

def delete_task(task_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
    conn.commit()
    conn.close()

def get_tasks():
    conn = get_conn()
    df = pd.read_sql("SELECT * FROM tasks", conn)
    conn.close()
    return df

# -----------------------
# UI Config
# -----------------------
st.set_page_config(
    page_title="Data Analyst To-Do List",
    page_icon="🧠",
    layout="wide"
)

# Initialize DB
init_db()

# Motivational Quotes (A/B Testing)
quotes_a = [
    "🚀 Stay focused and keep shipping!",
    "💡 Small progress every day leads to big results.",
    "🔥 Productivity is the bridge between goals and success."
]
quotes_b = [
    "Excellence is not an act, but a habit.",
    "Focus on being productive instead of busy.",
    "Your future is created by what you do today."
]
variant = random.choice(["A", "B"])
quote = random.choice(quotes_a if variant == "A" else quotes_b)

st.markdown(
    f"""<div style="
        background:#2c3e50;
        color:white;
        padding:15px;
        border-radius:10px;
        text-align:center;
        font-size:18px;
        font-weight:500;">
        {quote}
    </div>""",
    unsafe_allow_html=True
)

# -----------------------
# Sidebar: Add Task
# -----------------------
with st.sidebar:
    st.header("➕ Add New Task")
    new_title = st.text_input("Task")
    new_priority = st.selectbox("Priority", [1, 2, 3, 4, 5], index=2)
    new_tag = st.text_input("Category")
    new_due = st.date_input("Due Date", value=pd.to_datetime("today"))
    if st.button("Add Task"):
        if new_title.strip():
            add_task(new_title.strip(), new_priority, new_tag.strip(), str(new_due))
            st.success("Task added ✅")
            st.rerun()
        else:
            st.warning("Task title cannot be empty.")

# -----------------------
# Main Tabs
# -----------------------
tab1, tab2 = st.tabs(["📋 My Tasks", "📊 Analytics"])

# -----------------------
# Tab 1: Task List + Kanban
# -----------------------
with tab1:
    st.subheader("📋 All Tasks")
    df = get_tasks()

    if df.empty:
        st.info("No tasks yet. Add one from the sidebar ➡️")
    else:
        for _, row in df.iterrows():
            col1, col2, col3 = st.columns([4, 2, 1])
            with col1:
                st.write(f"**{row['title']}** (Priority {row['priority']})")
            with col2:
                new_status = st.selectbox(
                    "Status",
                    ["To Do", "In Progress", "Done"],
                    index=["To Do", "In Progress", "Done"].index(row["status"]),
                    key=f"status_{row['id']}"
                )
                if new_status != row["status"]:
                    update_status(row["id"], new_status)
                    if new_status == "Done":
                        st.balloons()
                    st.rerun()
            with col3:
                if st.button("🗑", key=f"del_{row['id']}"):
                    delete_task(row["id"])
                    st.success("Deleted ✅")
                    st.rerun()

    # Kanban View
    st.subheader("🗂 Kanban Board")
    cols = st.columns(3)
    statuses = ["To Do", "In Progress", "Done"]
    colors = {"To Do": "#f8d7da", "In Progress": "#fff3cd", "Done": "#d4edda"}

    for i, status in enumerate(statuses):
        with cols[i]:
            st.markdown(f"### {status}")
            for _, row in df[df["status"] == status].iterrows():
                due = "-"
                if row["due_date"]:
                    try:
                        due = pd.to_datetime(row["due_date"]).strftime("%b %d, %Y")
                    except:
                        due = row["due_date"]

                category_line = f"📂 Category: {row['tag']}<br>" if row["tag"] else ""

                st.markdown(
                    f"""
                    <div style="
                        background-color:{colors[status]};
                        color:#000000; 
                        padding:12px; 
                        border-radius:10px; 
                        margin-bottom:10px;
                        box-shadow: 0 2px 6px rgba(0,0,0,0.1);">
                        <b>✅ {row['title']}</b><br>
                        🔢 Priority: <b>{row['priority']}</b><br>
                        {category_line}
                        📅 {due}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

# -----------------------
# Tab 2: Analytics
# -----------------------
with tab2:
    st.subheader("📊 Productivity Analytics")
    df = get_tasks()

    if df.empty:
        st.info("No tasks available to analyze.")
    else:
        if "completed_at" not in df.columns:
            df["completed_at"] = None
        df["completed_at"] = pd.to_datetime(df["completed_at"], errors="coerce")
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")

        completion_rate = (df["status"] == "Done").mean() * 100
        st.metric("✅ Completion Rate", f"{completion_rate:.1f}%")

        done_tasks = df[df["status"] == "Done"].dropna(subset=["completed_at", "created_at"])
        if not done_tasks.empty:
            avg_time = (done_tasks["completed_at"] - done_tasks["created_at"]).mean()
            st.metric("⏱ Avg Completion Time", str(avg_time).split(".")[0])
        else:
            st.write("⏱ No completed tasks yet.")

        st.write("### Tasks by Priority")
        conn = get_conn()
        query1 = "SELECT priority, COUNT(*) as count FROM tasks GROUP BY priority"
        st.code(query1, language="sql")
        df_priority = pd.read_sql(query1, conn)
        conn.close()
        fig, ax = plt.subplots()
        ax.bar(df_priority["priority"], df_priority["count"])
        ax.set_xlabel("Priority")
        ax.set_ylabel("Number of Tasks")
        st.pyplot(fig)

        st.write("### Tasks by Category")
        conn = get_conn()
        query2 = "SELECT tag, COUNT(*) as count FROM tasks GROUP BY tag"
        st.code(query2, language="sql")
        df_tag = pd.read_sql(query2, conn)
        conn.close()
        fig, ax = plt.subplots()
        ax.bar(df_tag["tag"], df_tag["count"])
        ax.set_xlabel("Category")
        ax.set_ylabel("Number of Tasks")
        st.pyplot(fig)

        st.write("### Weekly Completion Trend")
        if not done_tasks.empty:
            trend = done_tasks.groupby(done_tasks["completed_at"].dt.to_period("W")).size()
            fig, ax = plt.subplots()
            trend.plot(kind="line", ax=ax, marker="o")
            ax.set_ylabel("Completed Tasks")
            st.pyplot(fig)
