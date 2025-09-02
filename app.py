import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import random
from datetime import datetime

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(page_title="Data Analyst To-Do List", page_icon="🧠", layout="wide")

# --------------------------------------------------
# Session State for Messages and Rerun Flag
# --------------------------------------------------
if "task_message" not in st.session_state:
    st.session_state["task_message"] = ""
if "rerun_flag" not in st.session_state:
    st.session_state["rerun_flag"] = False

# --------------------------------------------------
# Motivational Quotes
# --------------------------------------------------
quotes = [
    "🚀 Small steps every day lead to big results.",
    "🔥 Stay focused, the hard work will pay off.",
    "🌟 Progress, not perfection.",
    "💡 Every task you complete builds momentum.",
    "⏳ Don’t wait for inspiration, create it.",
    "🏆 Winners are ordinary people with extraordinary consistency.",
]
st.markdown(
    f"""
    <div style="background-color:#2E86C1;padding:15px;border-radius:10px;margin-bottom:20px;">
        <h3 style="color:white;text-align:center;font-weight:600;font-size:20px;">{random.choice(quotes)}</h3>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------
# Database Functions
# --------------------------------------------------
def get_conn():
    conn = sqlite3.connect("tasks.db", check_same_thread=False)
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            status TEXT DEFAULT 'To Do',
            priority INTEGER,
            tag TEXT,
            due_date TEXT,
            created_at TEXT,
            completed_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()

def add_task(title, priority, tag, due_date):
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute(
            "SELECT COUNT(*) FROM tasks WHERE title=? AND priority=?",
            (title, priority),
        )
        exists = c.fetchone()[0]

        if exists > 0:
            st.session_state["task_message"] = "⚠️ Task already exists with the same name and priority."
        else:
            task_id = str(datetime.now().timestamp()).replace(".", "")
            c.execute(
                "INSERT INTO tasks (id, title, status, priority, tag, due_date, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (task_id, title, "To Do", priority, tag, due_date, datetime.now().isoformat()),
            )
            conn.commit()
            st.session_state["task_message"] = "Task added ✅"
            st.session_state["rerun_flag"] = True

        conn.close()
    except Exception as e:
        st.session_state["task_message"] = f"⚠️ Could not add task: {e}"

def get_tasks():
    try:
        conn = get_conn()
        df = pd.read_sql_query("SELECT * FROM tasks", conn)
        conn.close()
        return df
    except Exception as e:
        st.session_state["task_message"] = f"⚠️ Could not fetch tasks: {e}"
        return pd.DataFrame()

def update_status(task_id, new_status):
    try:
        conn = get_conn()
        c = conn.cursor()
        if new_status == "Done":
            c.execute(
                "UPDATE tasks SET status=?, completed_at=? WHERE id=?",
                (new_status, datetime.now().isoformat(), task_id),
            )
        else:
            c.execute("UPDATE tasks SET status=? WHERE id=?", (new_status, task_id))
        conn.commit()
        conn.close()
        st.session_state["rerun_flag"] = True
    except Exception as e:
        st.session_state["task_message"] = f"⚠️ Could not update status: {e}"

def delete_task(task_id):
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
        conn.commit()
        conn.close()
        st.session_state["rerun_flag"] = True
    except Exception as e:
        st.session_state["task_message"] = f"⚠️ Could not delete task: {e}"

# --------------------------------------------------
# Initialize DB
# --------------------------------------------------
init_db()

# --------------------------------------------------
# Sidebar (Task Input)
# --------------------------------------------------
st.sidebar.header("➕ Add New Task")
with st.sidebar.form("task_form"):
    title = st.text_input("Task Title")
    priority = st.selectbox("Priority (1 = High, 5 = Low)", [1, 2, 3, 4, 5])
    tag = st.text_input("Category / Tag")
    due_date = st.date_input("Due Date")
    submitted = st.form_submit_button("Add Task")
    if submitted:
        if title.strip():
            add_task(title, priority, tag.strip(), str(due_date))
        else:
            st.session_state["task_message"] = "⚠️ Please enter a task title."

# Show message if exists
if st.session_state["task_message"]:
    st.info(st.session_state["task_message"])

# --------------------------------------------------
# Main Tabs
# --------------------------------------------------
tab1, tab2 = st.tabs(["📋 Task Board", "📊 Analytics"])

# --------------------------------------------------
# Task Board
# --------------------------------------------------
with tab1:
    st.header("📋 Your Tasks")
    df = get_tasks()

    if df.empty:
        st.info("No tasks yet. Add some from the sidebar!")
    else:
        colors = {
            "To Do": "#F5B7B1",
            "In Progress": "#F9E79F",
            "Done": "#ABEBC6"
        }

        for _, row in df.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([6, 2, 1])
                with col1:
                    st.markdown(
                        f"""
                        <div style="
                            padding:10px;margin-bottom:10px;
                            border-radius:10px;
                            background-color:{colors.get(row['status'], '#D6EAF8')};
                            color:#1B2631;">
                            <b>{row['title']}</b><br>
                            🔢 Priority: {row['priority']}<br>
                            🏷 Category: {row['tag'] if row['tag'] else '-'}<br>
                            📅 {row['due_date']}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with col2:
                    new_status = st.selectbox(
                        "Status",
                        ["To Do", "In Progress", "Done"],
                        index=["To Do", "In Progress", "Done"].index(row["status"]),
                        key=f"status_{row['id']}",
                    )
                    if new_status != row["status"]:
                        update_status(row["id"], new_status)
                        st.session_state["task_message"] = f"Task '{row['title']}' marked as {new_status}"

                with col3:
                    if st.button("🗑", key=f"del_{row['id']}"):
                        delete_task(row["id"])
                        st.session_state["task_message"] = f"Task '{row['title']}' deleted successfully ✅"

# --------------------------------------------------
# Analytics
# --------------------------------------------------
with tab2:
    st.header("📊 Task Analytics")
    df = get_tasks()

    if df.empty:
        st.info("No data to analyze yet. Add tasks first!")
    else:
        try:
            df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
            df["completed_at"] = pd.to_datetime(df["completed_at"], errors="coerce")

            # Stats
            total = len(df)
            done = len(df[df["status"] == "Done"])
            in_progress = len(df[df["status"] == "In Progress"])
            todo = len(df[df["status"] == "To Do"])

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Tasks", total)
            col2.metric("✅ Done", done)
            col3.metric("🚧 In Progress", in_progress)
            col4.metric("📌 To Do", todo)

            # Pie Chart
            status_counts = df["status"].value_counts()
            fig, ax = plt.subplots()
            ax.pie(status_counts, labels=status_counts.index, autopct="%1.1f%%", startangle=90)
            ax.axis("equal")
            st.pyplot(fig)

            # Completion Over Time
            if "completed_at" in df and not df["completed_at"].isna().all():
                completed_over_time = df.dropna(subset=["completed_at"]).groupby(
                    df["completed_at"].dt.date
                ).size()
                st.line_chart(completed_over_time)

            # Download CSV
            st.download_button(
                "📥 Download Task Data (CSV)",
                df.to_csv(index=False),
                file_name="tasks.csv",
                mime="text/csv",
            )

        except Exception as e:
            st.session_state["task_message"] = f"⚠️ Could not generate analytics: {e}"

# --------------------------------------------------
# Rerun if flagged
# --------------------------------------------------
if st.session_state["rerun_flag"]:
    st.session_state["rerun_flag"] = False
    st.experimental_rerun()
