import streamlit as st
import pandas as pd
import sqlite3
import random
import matplotlib.pyplot as plt
from datetime import datetime

# --- Page Config ---
st.set_page_config(page_title="📌 To-Do List", layout="wide")

# --- Database Setup ---
conn = sqlite3.connect("tasks.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    status TEXT,
    priority INTEGER,
    tag TEXT,
    due_date TEXT,
    created_at TEXT,
    completed_at TEXT
)
""")
c.execute("""
CREATE TABLE IF NOT EXISTS experiments (
    user_group TEXT
)
""")
conn.commit()

# --- Assign User Group for A/B Test ---
c.execute("SELECT user_group FROM experiments LIMIT 1")
row = c.fetchone()
if row is None:
    group = random.choice(["fun", "pro"])
    c.execute("INSERT INTO experiments (user_group) VALUES (?)", (group,))
    conn.commit()
else:
    group = row[0]

# --- Motivational Quotes (A/B test) ---
fun_quotes = [
    "🚀 Start where you are. Use what you have. Do what you can.",
    "✅ Small steps every day lead to big results.",
    "🔥 Productivity is never an accident. It is the result of commitment."
]
pro_quotes = [
    "Discipline is the bridge between goals and accomplishment.",
    "Productivity is about working smarter, not harder.",
    "Success comes to those who prioritize effectively."
]
quote = random.choice(fun_quotes if group == "fun" else pro_quotes)

st.markdown(
    f"""
    <div style="background-color:#f0f2f6; padding:10px; border-radius:8px; text-align:center; font-size:18px;">
        <b>{quote}</b>
    </div>
    """,
    unsafe_allow_html=True
)

# --- Sidebar Task Input ---
st.sidebar.header("➕ Add New Task")
title = st.sidebar.text_input("Task Title")
priority = st.sidebar.selectbox("Priority (1 = Low, 5 = High)", [1, 2, 3, 4, 5])
tag = st.sidebar.text_input("Category")
due_date = st.sidebar.date_input("Due Date")
if st.sidebar.button("Add Task"):
    if title:
        c.execute(
            "INSERT INTO tasks (title, status, priority, tag, due_date, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (title, "To Do", priority, tag, str(due_date), datetime.now().isoformat())
        )
        conn.commit()
        st.sidebar.success("Task added!")

# --- Load Data ---
df = pd.read_sql("SELECT * FROM tasks", conn)

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📋 Task List", "🗂 Kanban Board", "📊 Analytics"])

# --- Task List ---
with tab1:
    st.header("📋 All Tasks")
    if df.empty:
        st.info("No tasks yet. Add some from the sidebar ➕")
    else:
        for _, row in df.iterrows():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{row['title']}** (Priority {row['priority']}) — {row['status']}")
            with col2:
                new_status = st.selectbox(
                    "Update Status",
                    ["To Do", "In Progress", "Done"],
                    index=["To Do", "In Progress", "Done"].index(row["status"]),
                    key=f"status_{row['id']}"
                )
                if new_status != row["status"]:
                    completed_at = datetime.now().isoformat() if new_status == "Done" else None
                    c.execute("UPDATE tasks SET status=?, completed_at=? WHERE id=?",
                              (new_status, completed_at, row["id"]))
                    conn.commit()
                    st.experimental_set_query_params()  # refresh

# --- Kanban Board ---
with tab2:
    st.header("🗂 Kanban Board")
    if df.empty:
        st.info("No tasks yet.")
    else:
        cols = st.columns(3)
        statuses = ["To Do", "In Progress", "Done"]
        colors = {"To Do": "#FFF3CD", "In Progress": "#CCE5FF", "Done": "#D4EDDA"}
        for i, status in enumerate(statuses):
            with cols[i]:
                st.subheader(status)
                for _, row in df[df["status"] == status].iterrows():
                    # format due date
                    due = "-"
                    if row["due_date"]:
                        try:
                            due = pd.to_datetime(row["due_date"]).strftime("%b %d, %Y")
                        except:
                            due = row["due_date"]
                    # optional category
                    category_line = f"📂 Category: {row['tag']}<br>" if row["tag"] else ""
                    # build task card
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

# --- Analytics ---
with tab3:
    st.header("📊 Task Insights")
    if df.empty:
        st.info("No data yet. Add tasks to see analytics.")
    else:
        # Completion progress
        total_tasks = len(df)
        done_tasks = len(df[df["status"] == "Done"])
        progress = done_tasks / total_tasks if total_tasks > 0 else 0
        st.subheader("✅ Overall Progress")
        st.progress(progress)
        st.write(f"{done_tasks} of {total_tasks} tasks completed")

        # Average completion time
        df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
        df["completed_at"] = pd.to_datetime(df["completed_at"], errors="coerce")
        completed = df.dropna(subset=["completed_at"])
        if not completed.empty:
            avg_time = (completed["completed_at"] - completed["created_at"]).mean()
            st.write(f"⏱ Avg. completion time: {avg_time.days} days")
        else:
            st.write("⏱ No completed tasks yet to calculate average time.")

        col1, col2 = st.columns(2)

        # Tasks by priority
        with col1:
            st.subheader("🔢 Tasks by Priority")
            sql_q = "SELECT priority, COUNT(*) as count FROM tasks GROUP BY priority"
            st.caption(f"SQL: {sql_q}")
            fig, ax = plt.subplots()
            df["priority"].value_counts().sort_index().plot(
                kind="bar", ax=ax, color="skyblue", edgecolor="black"
            )
            ax.set_xlabel("Priority")
            ax.set_ylabel("Count")
            st.pyplot(fig)
            st.info("Insight: Most of your tasks fall into mid-level priority. Consider balancing workload.")

        # Tasks by category
        with col2:
            st.subheader("📂 Tasks by Category")
            sql_q = "SELECT tag, COUNT(*) as count FROM tasks GROUP BY tag"
            st.caption(f"SQL: {sql_q}")
            if df["tag"].notna().any():
                fig, ax = plt.subplots()
                df["tag"].value_counts().plot(
                    kind="bar", ax=ax, color="lightgreen", edgecolor="black"
                )
                ax.set_ylabel("Count")
                st.pyplot(fig)
                st.info("Insight: Your most common category is where you’re spending most effort.")
            else:
                st.write("No categories assigned yet.")

        # Weekly completion trend
        st.subheader("📅 Weekly Completion Trend")
        sql_q = "SELECT due_date, COUNT(*) FROM tasks WHERE status='Done' GROUP BY strftime('%W', due_date)"
        st.caption(f"SQL: {sql_q}")
        df["due_date"] = pd.to_datetime(df["due_date"], errors="coerce")
        trend = df[df["status"] == "Done"].groupby(df["due_date"].dt.isocalendar().week).size()
        if not trend.empty:
            fig, ax = plt.subplots()
            trend.plot(kind="line", marker="o", ax=ax)
            ax.set_xlabel("Week")
            ax.set_ylabel("Completed Tasks")
            st.pyplot(fig)
            st.info("Insight: Track how your weekly productivity is trending over time.")
        else:
            st.write("No completed tasks yet.")
