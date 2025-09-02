import streamlit as st
import pandas as pd
import sqlite3
import uuid
import random
from datetime import datetime

# --------------------------
# DB SETUP
# --------------------------
DB_FILE = "tasks.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
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
    # schema migration (add missing cols if old DB exists)
    existing_cols = [row[1] for row in c.execute("PRAGMA table_info(tasks)")]
    if "tag" not in existing_cols:
        c.execute("ALTER TABLE tasks ADD COLUMN tag TEXT")
    if "priority" not in existing_cols:
        c.execute("ALTER TABLE tasks ADD COLUMN priority INTEGER DEFAULT 3")
    if "due_date" not in existing_cols:
        c.execute("ALTER TABLE tasks ADD COLUMN due_date TEXT")
    conn.commit()
    conn.close()

def add_task(title, priority, tag, due_date):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO tasks VALUES (?,?,?,?,?,?,?)", (
        str(uuid.uuid4()),
        title,
        "To Do",
        priority,
        tag,
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        due_date
    ))
    conn.commit()
    conn.close()

def get_tasks():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM tasks", conn)
    conn.close()
    return df

def update_status(task_id, status):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("UPDATE tasks SET status=? WHERE id=?", (status, task_id))
    conn.commit()
    conn.close()

# --------------------------
# APP UI
# --------------------------
st.set_page_config(page_title="📋 To-Do List", layout="wide")

st.title("📋 To-Do List App")

# --- Motivation Quotes ---
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
st.info(f"💬 **Motivation for Today:** {random.choice(QUOTES)}")
st.markdown("---")

init_db()

# --------------------------
# SIDEBAR: ADD NEW TASK
# --------------------------
st.sidebar.header("➕ Add a new task")
with st.sidebar.form("new_task_form", clear_on_submit=True):
    title = st.text_input("Task")
    priority = st.slider("Priority (1 = Low, 5 = High)", 1, 5, 3)
    tag = st.text_input("Tag (optional)")
    due_date = st.date_input("Due Date", value=None)
    submitted = st.form_submit_button("Add Task")
    if submitted and title.strip():
        add_task(title.strip(), priority, tag, due_date.strftime("%Y-%m-%d") if due_date else "")
        st.sidebar.success("Task added!")
        st.rerun()

# --------------------------
# MAIN TABS
# --------------------------
df = get_tasks()
tab1, tab2, tab3 = st.tabs(["📋 List View", "🗂 Kanban Board", "📊 Analytics"])

# --- List View ---
with tab1:
    st.header("📋 Task List")
    if df.empty:
        st.info("No tasks yet.")
    else:
        expected_cols = ["id","title","status","priority","tag","due_date"]
        for col in expected_cols:
            if col not in df.columns:
                df[col] = ""
        for _, row in df.iterrows():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
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
                    update_status(row["id"], new_status)
                    st.rerun()
            with col3:
                st.markdown(f"🔢 Priority: **{row['priority']}**")
            with col4:
                st.markdown(f"🏷 {row['tag'] if row['tag'] else '-'}")

# --- Kanban View ---
# --- Kanban View ---
with tab2:
    st.header("🗂 Kanban Board")
    if df.empty:
        st.info("No tasks yet.")
    else:
        cols = st.columns(3)
        statuses = ["To Do", "In Progress", "Done"]
        colors = {
            "To Do": "#FFF3CD",          # soft yellow
            "In Progress": "#CCE5FF",    # soft blue
            "Done": "#D4EDDA"            # soft green
        }
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

                    # build task card with dark text
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
                            🏷 {row['tag'] if row['tag'] else '-'}<br>
                            📅 {due}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )



# --- Analytics View ---
with tab3:
    st.header("📊 Analytics")
    if df.empty:
        st.info("No data to analyze yet.")
    else:
        total = len(df)
        done = len(df[df["status"]=="Done"])
        st.metric("✅ Completion Rate", f"{(done/total*100):.1f}%")

        st.subheader("Task Status Distribution")
        st.bar_chart(df["status"].value_counts())

        st.subheader("Tasks by Priority")
        st.bar_chart(df["priority"].value_counts().sort_index())

        st.subheader("Tasks by Tag")
        tag_counts = df["tag"].fillna("Untagged").replace("", "Untagged").value_counts()
        st.bar_chart(tag_counts)
