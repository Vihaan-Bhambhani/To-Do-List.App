import streamlit as st
import pandas as pd
import sqlite3
import random
import matplotlib.pyplot as plt
from datetime import datetime, date

DB_FILE = "tasks.db"

# ------------------------------
# DB helpers + migration
# ------------------------------
def get_conn():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def ensure_schema():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        status TEXT
    )
    """)
    adds = {
        "priority": "ALTER TABLE tasks ADD COLUMN priority INTEGER DEFAULT 3",
        "tag": "ALTER TABLE tasks ADD COLUMN tag TEXT DEFAULT ''",
        "due_date": "ALTER TABLE tasks ADD COLUMN due_date TEXT DEFAULT ''",
        "created_at": "ALTER TABLE tasks ADD COLUMN created_at TEXT DEFAULT ''",
        "completed_at": "ALTER TABLE tasks ADD COLUMN completed_at TEXT DEFAULT ''"
    }
    existing = [row[1] for row in c.execute("PRAGMA table_info(tasks)").fetchall()]
    for col, sql in adds.items():
        if col not in existing:
            try:
                c.execute(sql)
            except Exception:
                pass
    conn.commit()
    conn.close()

def ensure_experiments_table():
    conn = get_conn()
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS experiments (user_group TEXT)")
    conn.commit()
    conn.close()

# ------------------------------
# App functions
# ------------------------------
def assign_user_group():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT user_group FROM experiments LIMIT 1")
    row = c.fetchone()
    if row is None:
        group = random.choice(["fun", "pro"])
        c.execute("INSERT INTO experiments (user_group) VALUES (?)", (group,))
        conn.commit()
    else:
        group = row[0]
    conn.close()
    return group

def add_task(title, priority, tag, due_date):
    conn = get_conn()
    c = conn.cursor()
    created = datetime.now().isoformat()
    c.execute(
        "INSERT INTO tasks (title, status, priority, tag, due_date, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (title, "To Do", int(priority), tag or "", str(due_date) if due_date else "", created)
    )
    conn.commit()
    conn.close()

def update_task_status(task_id, new_status):
    conn = get_conn()
    c = conn.cursor()
    completed_at = datetime.now().isoformat() if new_status == "Done" else None
    c.execute("UPDATE tasks SET status=?, completed_at=? WHERE id=?", (new_status, completed_at, int(task_id)))
    conn.commit()
    conn.close()

def fetch_tasks_df():
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM tasks", conn)
    conn.close()
    expected_cols = ["id","title","status","priority","tag","due_date","created_at","completed_at"]
    for col in expected_cols:
        if col not in df.columns:
            df[col] = pd.NA
    return df

# ------------------------------
# Init
# ------------------------------
ensure_schema()
ensure_experiments_table()
group = assign_user_group()

# motivational quote A/B test
fun_quotes = [
    "🚀 Start where you are. Use what you have. Do what you can.",
    "✅ Small steps every day lead to big results.",
    "🔥 Push yourself; results follow consistent action."
]
pro_quotes = [
    "Discipline is the bridge between goals and accomplishment.",
    "Productivity is about working smarter, not harder.",
    "Focus on impactful work; measure progress."
]
quote = random.choice(fun_quotes if group == "fun" else pro_quotes)

st.set_page_config(page_title="📌 To-Do List (Data Analyst Demo)", layout="wide")
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

# ------------------------------
# Sidebar - Add Task
# ------------------------------
st.sidebar.header("➕ Add New Task")
title = st.sidebar.text_input("Task Title")
priority = st.sidebar.selectbox("Priority (1 = Low, 5 = High)", [1,2,3,4,5], index=2)
tag = st.sidebar.text_input("Category / Tag (optional)")
due_date = st.sidebar.date_input("Due Date (optional)", value=None)
if st.sidebar.button("Add Task"):
    if title and title.strip():
        add_task(title.strip(), priority, tag.strip(), due_date if due_date else "")
        st.sidebar.success("Task added!")
        st.rerun()
    else:
        st.sidebar.warning("Enter a task title before adding.")

# ------------------------------
# Load data
# ------------------------------
df = fetch_tasks_df()
df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")
df["completed_at"] = pd.to_datetime(df["completed_at"], errors="coerce")
df["due_date_parsed"] = pd.to_datetime(df["due_date"], errors="coerce")

# ------------------------------
# Main tabs
# ------------------------------
tab_list, tab_kanban, tab_analytics = st.tabs(["📋 Task List","🗂 Kanban","📊 Analytics"])

# -------- Task List --------
with tab_list:
    st.header("📋 Task List")
    if df.empty:
        st.info("No tasks yet. Add some from the sidebar.")
    else:
        for _, row in df.iterrows():
            cols = st.columns([4,2,2,2])
            with cols[0]:
                st.markdown(f"**{row['title']}**")
                meta = []
                if not pd.isna(row['priority']): meta.append(f"Priority: {int(row['priority'])}")
                if row['tag'] and not pd.isna(row['tag']): meta.append(f"Category: {row['tag']}")
                if not pd.isna(row['due_date_parsed']): meta.append(f"Due: {row['due_date_parsed'].date().isoformat()}")
                if meta:
                    st.markdown("<div style='color:#666;font-size:13px'>" + " • ".join(meta) + "</div>", unsafe_allow_html=True)
            with cols[1]:
                try:
                    current_status = row['status'] if not pd.isna(row['status']) else "To Do"
                    new_status = st.selectbox(
                        "",
                        ["To Do","In Progress","Done"],
                        index=["To Do","In Progress","Done"].index(current_status),
                        key=f"status_{row['id']}"
                    )
                except Exception:
                    new_status = st.selectbox("", ["To Do","In Progress","Done"], index=0, key=f"status_{row['id']}")
                if new_status != row['status']:
                    update_task_status(row['id'], new_status)
                    if new_status == "Done":
                        st.balloons()  # 🎉 confetti animation
                    st.rerun()
            with cols[2]:
                if st.button("🗑 Delete", key=f"del_{row['id']}"):
                    if pd.notna(row['id']):
                        conn = get_conn()
                        c = conn.cursor()
                        c.execute("DELETE FROM tasks WHERE id=?", (int(row['id']),))
                        conn.commit()
                        conn.close()
                        st.success("Deleted")
                        st.rerun()
                    else:
                        st.error("⚠️ Could not delete this task (invalid ID).")
            with cols[3]:
                st.write("")

# -------- Kanban --------
with tab_kanban:
    st.header("🗂 Kanban Board")
    if df.empty:
        st.info("No tasks yet.")
    else:
        statuses = ["To Do","In Progress","Done"]
        cols = st.columns(3)
        colors = {"To Do":"#FFF3CD","In Progress":"#CCE5FF","Done":"#D4EDDA"}
        for i, status in enumerate(statuses):
            with cols[i]:
                st.subheader(status)
                subset = df[df["status"] == status]
                if subset.empty:
                    st.info("—")
                for _, row in subset.iterrows():
                    due = "-"
                    if not pd.isna(row["due_date_parsed"]):
                        due = row["due_date_parsed"].strftime("%b %d, %Y")
                    category_line = f"<div style='margin-top:6px'>📂 <b>Category:</b> {row['tag']}</div>" if row['tag'] and not pd.isna(row['tag']) and row['tag']!="" else ""
                    pr = int(row['priority']) if not pd.isna(row['priority']) else 3
                    if pr >= 5:
                        pr_color = "#b91c1c"
                    elif pr >= 4:
                        pr_color = "#f97316"
                    elif pr == 3:
                        pr_color = "#f59e0b"
                    elif pr == 2:
                        pr_color = "#10b981"
                    else:
                        pr_color = "#059669"

                    st.markdown(
                        f"""
                        <div style="
                            background:{colors[status]};
                            color:#000;
                            padding:12px;
                            border-radius:10px;
                            margin-bottom:10px;
                            box-shadow: 0 2px 6px rgba(0,0,0,0.08);">
                            <div style="font-weight:600; font-size:15px">✅ {row['title']}</div>
                            <div style="margin-top:6px; font-size:13px">
                                <span style="color:{pr_color}; font-weight:700;">🔢 Priority: {pr}</span>
                                {'&nbsp;&nbsp;'}<span style="color:#374151">📅 {due}</span>
                            </div>
                            {category_line}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

# -------- Analytics --------
with tab_analytics:
    st.header("📊 Analytics & Insights")
    if df.empty:
        st.info("No data yet.")
    else:
        total = len(df)
        done = len(df[df["status"]=="Done"])
        progress = done / total if total else 0
        st.subheader("✅ Progress")
        st.progress(progress)
        st.write(f"{done} of {total} tasks completed ({progress*100:.1f}%)")

        completed = df.dropna(subset=["completed_at"])
        if not completed.empty:
            completed["completed_at"] = pd.to_datetime(completed["completed_at"], errors="coerce")
            completed["created_at"] = pd.to_datetime(completed["created_at"], errors="coerce")
            completed["duration_days"] = (completed["completed_at"] - completed["created_at"]).dt.total_seconds() / 86400
            avg_days = completed["duration_days"].mean()
            st.write(f"⏱ Average time to complete tasks: {avg_days:.2f} days")
        else:
            st.write("⏱ No completed tasks to calculate average completion time.")

        c1, c2 = st.columns(2)

        with c1:
            st.subheader("🔢 Tasks by Priority")
            sql_q = "SELECT priority, COUNT(*) FROM tasks GROUP BY priority"
            st.caption(f"SQL: {sql_q}")
            pr_counts = df["priority"].fillna(3).astype(int).value_counts().sort_index()
            fig, ax = plt.subplots()
            pr_counts.plot(kind="bar", ax=ax, color="skyblue", edgecolor="black")
            ax.set_xlabel("Priority (1=Low,5=High)")
            ax.set_ylabel("Count")
            st.pyplot(fig)
            top_pr = pr_counts.idxmax()
            st.info(f"Insight: Most tasks are at priority {top_pr}.")

        with c2:
            st.subheader("📂 Tasks by Category")
            sql_q2 = "SELECT tag, COUNT(*) FROM tasks GROUP BY tag"
            st.caption(f"SQL: {sql_q2}")
            tag_series = df["tag"].fillna("Untagged").replace("", "Untagged").value_counts()
            if not tag_series.empty:
                fig2, ax2 = plt.subplots()
                tag_series.plot(kind="bar", ax=ax2, color="lightgreen", edgecolor="black")
                ax2.set_ylabel("Count")
                st.pyplot(fig2)
                top_tag = tag_series.idxmax()
                st.info(f"Insight: You spend most effort on: {top_tag}")
            else:
                st.write("No categories assigned yet.")

        st.subheader("📅 Weekly Completion Trend")
        df["completed_at_dt"] = pd.to_datetime(df["completed_at"], errors="coerce")
        df["week"] = df["completed_at_dt"].dt.isocalendar().week
        weekly = df[df["status"]=="Done"].groupby("week").size()
        if not weekly.empty:
            fig3, ax3 = plt.subplots()
            weekly.plot(kind="line", marker="o", ax=ax3)
            ax3.set_xlabel("ISO Week Number")
            ax3.set_ylabel("Completed Tasks")
            st.pyplot(fig3)
            st.info("Track weekly completion to measure productivity trends.")
        else:
            st.write("No completed tasks yet.")
