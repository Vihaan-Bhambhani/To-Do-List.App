import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
from datetime import datetime
import os
import hashlib

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
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None
if "auth_action" not in st.session_state:
    st.session_state["auth_action"] = "login"

# --------------------------------------------------
# Utility Functions
# --------------------------------------------------
USERS_FILE = "users.csv"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if os.path.exists(USERS_FILE):
        return pd.read_csv(USERS_FILE)
    else:
        df = pd.DataFrame(columns=["username","password"])
        df.to_csv(USERS_FILE,index=False)
        return df

def save_users(df):
    df.to_csv(USERS_FILE,index=False)

def user_exists(username):
    df = load_users()
    return username.lower() in df["username"].str.lower().values

def validate_user(username, password):
    df = load_users()
    matches = df[df["username"].str.lower() == username.lower()]
    if matches.empty:
        return "not_registered"
    elif matches.iloc[0]["password"] != hash_password(password):
        return "wrong_password"
    else:
        return "ok"

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
# Sidebar Authentication
# --------------------------------------------------
st.sidebar.header("🔑 User Login / Registration")

auth_action = st.sidebar.radio("Action:", ["Login", "Register"])
st.session_state["auth_action"] = auth_action

username = st.sidebar.text_input("Username")
password = st.sidebar.text_input("Password", type="password")

if auth_action == "Register":
    confirm_password = st.sidebar.text_input("Confirm Password", type="password")
    if st.sidebar.button("Register"):
        if not username.strip() or not password:
            st.session_state["task_message"] = "⚠️ Username and password cannot be empty."
        elif password != confirm_password:
            st.session_state["task_message"] = "⚠️ Passwords do not match."
        elif user_exists(username):
            st.session_state["task_message"] = "⚠️ Username already exists."
        else:
            df = load_users()
            df = pd.concat([df, pd.DataFrame([{"username": username.lower(), "password": hash_password(password)}])], ignore_index=True)
            save_users(df)
            st.session_state["current_user"] = username.lower()
            st.session_state["task_message"] = f"✅ User '{username}' registered and logged in."
            st.session_state["rerun_flag"] = True

elif auth_action == "Login":
    if st.sidebar.button("Login"):
        if not username.strip() or not password:
            st.session_state["task_message"] = "⚠️ Enter both username and password."
        else:
            result = validate_user(username, password)
            if result == "not_registered":
                st.session_state["task_message"] = "⚠️ Username not registered."
            elif result == "wrong_password":
                st.session_state["task_message"] = "⚠️ Incorrect password."
            else:
                st.session_state["current_user"] = username.lower()
                st.session_state["task_message"] = f"✅ User '{username}' logged in."
                st.session_state["rerun_flag"] = True

# Show message if exists
if st.session_state["task_message"]:
    st.info(st.session_state["task_message"])

# --------------------------------------------------
# Only show tasks if logged in
# --------------------------------------------------
if st.session_state["current_user"] is not None:

    # --------------------------------------------------
    # File/DB Functions per User
    # --------------------------------------------------
    def user_file():
        return f"tasks_{st.session_state['current_user']}.csv"

    def init_user_file():
        f = user_file()
        if not os.path.exists(f):
            pd.DataFrame(columns=["id","title","status","priority","tag","due_date","created_at","completed_at"]).to_csv(f,index=False)

    def get_tasks():
        f = user_file()
        if os.path.exists(f):
            return pd.read_csv(f)
        else:
            return pd.DataFrame(columns=["id","title","status","priority","tag","due_date","created_at","completed_at"])

    def save_tasks(df):
        df.to_csv(user_file(),index=False)

    def add_task(title, priority, tag, due_date):
        try:
            df = get_tasks()
            # Duplicate check
            if ((df["title"].str.lower() == title.lower()) & (df["priority"] == priority)).any():
                st.session_state["task_message"] = "⚠️ Task already exists with same name and priority."
                return
            task_id = str(datetime.now().timestamp()).replace(".","")
            new_task = pd.DataFrame([{
                "id": task_id,
                "title": title,
                "status": "To Do",
                "priority": priority,
                "tag": tag,
                "due_date": due_date,
                "created_at": datetime.now().isoformat(),
                "completed_at": ""
            }])
            df = pd.concat([df,new_task],ignore_index=True)
            save_tasks(df)
            st.session_state["task_message"] = "✅ Task added"
            st.session_state["rerun_flag"] = True
        except Exception as e:
            st.session_state["task_message"] = f"⚠️ Could not add task: {e}"

    def update_status(task_id, new_status):
        try:
            df = get_tasks()
            idx = df.index[df["id"] == task_id]
            if len(idx) == 0:
                return
            idx = idx[0]
            df.at[idx,"status"] = new_status
            if new_status == "Done":
                df.at[idx,"completed_at"] = datetime.now().isoformat()
            save_tasks(df)
            st.session_state["rerun_flag"] = True
        except Exception as e:
            st.session_state["task_message"] = f"⚠️ Could not update status: {e}"

    def delete_task(task_id):
        try:
            df = get_tasks()
            df = df[df["id"] != task_id]
            save_tasks(df)
            st.session_state["rerun_flag"] = True
        except Exception as e:
            st.session_state["task_message"] = f"⚠️ Could not delete task: {e}"

    # --------------------------------------------------
    # Initialize user tasks file
    # --------------------------------------------------
    init_user_file()

    # --------------------------------------------------
    # Sidebar Add Task
    # --------------------------------------------------
    st.sidebar.header("➕ Add New Task")
    with st.sidebar.form("task_form"):
        title = st.text_input("Task Title")
        priority = st.selectbox("Priority (1 = High, 5 = Low)", [1,2,3,4,5])
        tag = st.text_input("Category / Tag")
        due_date = st.date_input("Due Date")
        submitted = st.form_submit_button("Add Task")
        if submitted:
            if title.strip():
                add_task(title, priority, tag.strip(), str(due_date))
            else:
                st.session_state["task_message"] = "⚠️ Please enter a task title."

    # --------------------------------------------------
    # Tabs
    # --------------------------------------------------
    tab1, tab2 = st.tabs(["📋 Task Board","📊 Analytics"])

    # --------------------------------------------------
    # Task Board
    # --------------------------------------------------
    with tab1:
        st.header(f"📋 Tasks for {st.session_state['current_user']}")
        df = get_tasks()
        if df.empty:
            st.info("No tasks yet. Add some from the sidebar!")
        else:
            colors = {"To Do":"#F5B7B1","In Progress":"#F9E79F","Done":"#ABEBC6"}
            for _, row in df.iterrows():
                with st.container():
                    col1,col2,col3 = st.columns([6,2,1])
                    with col1:
                        st.markdown(f"""
                            <div style="
                                padding:10px;margin-bottom:10px;
                                border-radius:10px;
                                background-color:{colors.get(row['status'],'#D6EAF8')};
                                color:#1B2631;">
                                <b>{row['title']}</b><br>
                                🔢 Priority: {row['priority']}<br>
                                🏷 Category: {row['tag'] if row['tag'] else '-'}<br>
                                📅 {row['due_date']}
                            </div>
                        """,unsafe_allow_html=True)
                    with col2:
                        new_status = st.selectbox(
                            "Status",["To Do","In Progress","Done"],
                            index=["To Do","In Progress","Done"].index(row["status"]),
                            key=f"status_{row['id']}")
                        if new_status != row["status"]:
                            update_status(row["id"], new_status)
                            st.session_state["task_message"] = f"Task '{row['title']}' marked as {new_status}"
                    with col3:
                        if st.button("🗑",key=f"del_{row['id']}"):
                            delete_task(row["id"])
                            st.session_state["task_message"] = f"Task '{row['title']}' deleted successfully ✅"

    # --------------------------------------------------
    # Analytics
    # --------------------------------------------------
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
            df["created_at"] = pd.to_datetime(df["created_at"],errors="coerce")
            df["completed_at"] = pd.to_datetime(df["completed_at"],errors="coerce")

            # Metrics
            total = len(df)
            done = len(df[df["status"]=="Done"])
            in_progress = len(df[df["status"]=="In Progress"])
            todo = len(df[df["status"]=="To Do"])

            col1,col2,col3,col4 = st.columns(4)
            col1.metric("Total Tasks",total)
            col2.metric("✅ Done",done)
            col3.metric("🚧 In Progress",in_progress)
            col4.metric("📌 To Do",todo)

            # Pie Chart
            status_counts = df["status"].value_counts()
            fig, ax = plt.subplots()
            ax.pie(status_counts,labels=status_counts.index,autopct="%1.1f%%",startangle=90)
            ax.axis("equal")
            st.pyplot(fig)

            # Completion Over Time
            if "completed_at" in df and not df["completed_at"].isna().all():
                completed_over_time = df.dropna(subset=["completed_at"]).groupby(df["completed_at"].dt.date).size()
                st.line_chart(completed_over_time)

            # Download CSV
            st.download_button(
                "📥 Download Task Data (CSV)",
                df.to_csv(index=False),
                file_name=f"tasks_{st.session_state['current_user']}.csv",
                mime="text/csv"
            )

        except Exception as e:
            st.session_state["task_message"] = f"⚠️ Could not generate analytics: {e}"
