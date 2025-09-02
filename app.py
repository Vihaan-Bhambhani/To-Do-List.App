import streamlit as st
import sqlite3
import pandas as pd
import uuid
from datetime import datetime, date, timedelta
import dateparser
import matplotlib.pyplot as plt
import random

DB_FILE = "tasks.db"

# ---------------- DB Helpers ----------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Create table if not exists
    c.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        title TEXT,
        status TEXT,
        priority INTEGER,
        tag TEXT,
        created_at TEXT,
        due_date TEXT
    )
    """)
    # Ensure new columns exist (migration)
    existing_cols = [row[1] for row in c.execute("PRAGMA table_info(tasks)")]
    if "priority" not in existing_cols:
        c.execute("ALTER TABLE tasks ADD COLUMN priority INTEGER DEFAULT 3")
    if "tag" not in existing_cols:
        c.execute("ALTER TABLE tasks ADD COLUMN tag TEXT DEFAULT ''")
    if "due_date" not in existing_cols:
        c.execute("ALTER TABLE tasks ADD COLUMN due_date TEXT DEFAULT ''")
    conn.commit()
    conn.close()

def add_task(title, status="To Do", priority=3, tag="", due_date=""):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    tid = str(uuid.uuid4())
    created = datetime.utcnow().isoformat()
    c.execute("INSERT INTO tasks VALUES (?,?,?,?,?,?,?)",
              (tid, title, status, priority, tag, created, due_date))
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

# ---------------- Helper Functions ----------------
priority_labels = {
    1: "🔴 Urgent",
    2: "🟠 High",
    3: "🟡 Medium",
    4: "🔵 Low",
    5: "🟢 Very Low"
}

def parse_natural_input(text):
    """Parse natural language task input like 'meeting tomorrow high priority'"""
    if not text.strip():
        return None, None, None
    parsed_date = dateparser.parse(text, settings={"PREFER_DATES_FROM": "future"})
    due_date = parsed_date.date().isoformat() if parsed_date else ""
    # Priority detection
    prio = 3
    if "urgent" in text.lower() or "p1" in text.lower():
        prio = 1
    elif "high" in text.lower() or "p2" in text.lower():
        prio = 2
    elif "low" in text.lower() or "p4" in text.lower():
        prio = 4
    elif "very low" in text.lower() or "p5" in text.lower():
        prio = 5
    return text, prio, due_date

# ---------------- Streamlit UI ----------------
st.set_page_config(page_title="📝 Smart To-Do", page_icon="✅", layout="wide")

st.title("✅ Smart To-Do List with Analytics")


# Motivational quotes
QUOTES = [
    "🌟 Believe you can and you're halfway there.",
    "🚀 Small progress each day adds up to big results.",
    "🔥 Push yourself, because no one else is going to do it for you.",
    "💡 Great things never come from comfort zones.",
    "✅ Don’t watch the clock; do what it does. Keep going.",
    "🏆 Success is the sum of small efforts repeated day in and day out.",
    "🌱 Every accomplishment starts with the decision to try."
]

st.markdown("---")
quote = random.choice(QUOTES)
st.info(f"💬 **Motivation for Today:** {quote}")
st.markdown("---")


init_db()
df = fetch_tasks()

# Sidebar: Add task
st.sidebar.header("➕ Add Task")
mode = st.sidebar.radio("Add Mode", ["Manual", "Natural Language"])

if mode == "Manual":
    title = st.sidebar.text_input("Task")
    priority = st.sidebar.selectbox("Priority (1=high, 5=low)", [1,2,3,4,5], index=2)
    tag = st.sidebar.text_input("Tag (optional)")
    due_date = st.sidebar.date_input("Due Date", value=None)
    if st.sidebar.button("Add Task"):
        if title.strip():
            due_str = due_date.isoformat() if due_date else ""
            add_task(title, "To Do", priority, tag, due_str)
            st.sidebar.success("Task added!")
            st.rerun()
        else:
            st.sidebar.warning("Please enter a task title!")
else:
    nl_text = st.sidebar.text_area("Enter task naturally (e.g., 'Finish report tomorrow high priority')")
    tag = st.sidebar.text_input("Tag (optional)")
    if st.sidebar.button("Parse & Add"):
        parsed_title, parsed_priority, parsed_due = parse_natural_input(nl_text)
        if parsed_title:
            add_task(parsed_title, "To Do", parsed_priority, tag, parsed_due)
            st.sidebar.success(f"Task added with priority {parsed_priority} and due {parsed_due or '—'}")
            st.rerun()

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["📋 List View", "🗂 Kanban", "📆 Calendar", "📊 Analytics"])

# --- List View ---
with tab1:
    st.header("📋 Task List")
    if df.empty:
        st.info("No tasks yet.")
    else:
        # Backward compatibility: fill missing columns
        expected_cols = ["title","status","priority","tag","due_date"]
        for col in expected_cols:
            if col not in df.columns:
                df[col] = ""
        #st.dataframe(df[expected_cols])
        for _, row in df.iterrows():
            col1, col2, col3 = st.columns([3, 2, 2])
            with col1:
                st.markdown(f"**{row['title']}**")
            with col2:
                new_status = st.selectbox(
                    "Status",
                    ["To Do", "In Progress", "Done"],
                    index=["To Do", "In Progress", "Done"].index(row["status"]),
                    key=f"status_{row['id']}"
                )
                if new_status != row["status"]:
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    c.execute("UPDATE tasks SET status=? WHERE id=?", (new_status, row["id"]))
                    conn.commit()
                    conn.close()
                    st.experimental_rerun()
            with col3:
                st.markdown(f"🔢 Priority: **{row['priority']}**")


# --- Kanban View ---
with tab2:
    st.header("🗂 Kanban Board")
    statuses = ["To Do", "In Progress", "Done"]
    cols = st.columns(3)
    for i, status in enumerate(statuses):
        with cols[i]:
            st.subheader(status)
            tasks = df[df["status"] == status]
            if tasks.empty:
                st.info("No tasks")
            for _, row in tasks.iterrows():
                st.markdown(
                    f"**{row['title']}**  \n"
                    f"🏷️ {priority_labels.get(row['priority'], row['priority'])}  \n"
                    f"🔖 {row['tag'] or '—'}  \n"
                    f"📅 {row['due_date'] or '—'}",
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
                st.markdown("---")

# --- Calendar View ---
with tab3:
    st.header("📆 Calendar View")
    if df.empty:
        st.info("No tasks yet.")
    else:
        if "due_date" in df and df["due_date"].notna().any():
            grouped = df[df["due_date"] != ""].groupby("due_date")["title"].apply(list)
            for d, tasks in grouped.items():
                st.subheader(f"📅 {d}")
                for t in tasks:
                    st.write(f"- {t}")
        else:
            st.info("No tasks with due dates.")

# --- Analytics View ---
with tab4:
    st.header("📊 Analytics Dashboard")
    if df.empty:
        st.info("No tasks to analyze.")
    else:
        # KPIs
        overdue = len(df[(df["due_date"] != "") & (pd.to_datetime(df["due_date"]) < pd.to_datetime(date.today())) & (df["status"] != "Done")])
        done = len(df[df["status"]=="Done"])
        total = len(df)
        today_tasks = len(df[(df["due_date"] == str(date.today()))])
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Tasks", total)
        col2.metric("Completed", done)
        col3.metric("Overdue", overdue)
        col4.metric("Due Today", today_tasks)

        # Chart: Tasks by Priority
        st.subheader("Tasks by Priority")
        fig, ax = plt.subplots()
        df["priority"].value_counts().sort_index().plot(kind="bar", ax=ax)
        ax.set_xlabel("Priority")
        ax.set_ylabel("Count")
        st.pyplot(fig)

        # Chart: Status Distribution
        st.subheader("Task Status Distribution")
        fig2, ax2 = plt.subplots()
        df["status"].value_counts().plot(kind="pie", autopct="%1.0f%%", ax=ax2)
        ax2.set_ylabel("")
        st.pyplot(fig2)

        # Chart: Tasks over Time
        st.subheader("Tasks Created Over Time")
        df["created_at"] = pd.to_datetime(df["created_at"])
        tasks_over_time = df.groupby(df["created_at"].dt.date).size()
        fig3, ax3 = plt.subplots()
        tasks_over_time.plot(kind="line", marker="o", ax=ax3)
        ax3.set_xlabel("Date")
        ax3.set_ylabel("Tasks Added")
        st.pyplot(fig3)

        # Gamification: Streaks
        st.subheader("🔥 Productivity Streak")
        if not df[df["status"]=="Done"].empty:
            done_dates = df[df["status"]=="Done"]["created_at"].dt.date.unique()
            done_dates = sorted(done_dates)
            streak, max_streak = 1, 1
            for i in range(1, len(done_dates)):
                if (done_dates[i] - done_dates[i-1]) == timedelta(days=1):
                    streak += 1
                    max_streak = max(max_streak, streak)
                else:
                    streak = 1
            st.write(f"Current Streak: {streak} days")
            st.write(f"Best Streak: {max_streak} days")
        else:
            st.info("No completed tasks yet.")
