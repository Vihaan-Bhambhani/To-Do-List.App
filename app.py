import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
from datetime import datetime
import os
import hashlib

# ------------------- Page Config -------------------
st.set_page_config(
    page_title="Data Analyst To-Do List",
    page_icon="🧠",
    layout="centered"
)

# ------------------- Session State -------------------
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "task_message" not in st.session_state:
    st.session_state["task_message"] = ""
if "rerun_needed" not in st.session_state:
    st.session_state["rerun_needed"] = False

# ------------------- Users CSV -------------------
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

# ------------------- Motivational Quotes -------------------
quotes = [
    "🚀 Small steps every day lead to big results.",
    "🔥 Stay focused, the hard work will pay off.",
    "🌟 Progress, not perfection.",
    "💡 Every task you complete builds momentum.",
    "⏳ Don’t wait for inspiration, create it.",
    "🏆 Winners are ordinary people with extraordinary consistency.",
]

# ------------------- Login/Register Page -------------------
if not st.session_state["logged_in"]:
    st.markdown("<h1 style='text-align:center'>🧠 Login / Register</h1>", unsafe_allow_html=True)
    action = st.radio("Action:", ["Login", "Register"], horizontal=True)

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        confirm_password = ""
        if action == "Register":
            confirm_password = st.text_input("Confirm Password", type="password")
        submitted = st.form_submit_button("Submit")

        if submitted:
            if not username.strip() or not password:
                st.warning("⚠️ Enter both username and password.")
            elif action == "Register" and password != confirm_password:
                st.warning("⚠️ Passwords do not match.")
            elif action == "Register" and user_exists(username):
                st.warning("⚠️ Username already exists.")
            elif action == "Register":
                df = load_users()
                df = pd.concat([df, pd.DataFrame([{"username": username.lower(), "password": hash_password(password)}])], ignore_index=True)
                save_users(df)
                st.session_state["current_user"] = username.lower()
                st.session_state["logged_in"] = True
                st.success(f"✅ User '{username}' registered and logged in!")
            elif action == "Login":
                result = validate_user(username, password)
                if result == "not_registered":
                    st.warning("⚠️ Username not registered.")
                elif result == "wrong_password":
                    st.warning("⚠️ Incorrect password.")
                else:
                    st.session_state["current_user"] = username.lower()
                    st.session_state["logged_in"] = True
                    st.success(f"✅ User '{username}' logged in!")

# ------------------- Main App -------------------
if st.session_state["logged_in"]:
    st.set_page_config(page_title="Data Analyst To-Do List", page_icon="🧠", layout="wide")

    # ------------------- User Task Functions -------------------
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
        df = get_tasks()
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
        st.session_state["rerun_needed"] = True

    def update_status(task_id, new_status):
        df = get_tasks()
        idx = df.index[df["id"] == task_id]
        if len(idx) == 0:
            return
        idx = idx[0]
        df.at[idx,"status"] = new_status
        if new_status == "Done":
            df.at[idx,"completed_at"] = datetime.now().isoformat()
        save_tasks(df)
        st.session_state["task_message"] = f"✅ Task '{df.at[idx,'title']}' status updated to {new_status}"
        st.session_state["rerun_needed"] = True

    def delete_task(task_id):
        df = get_tasks()
        df = df[df["id"] != task_id]
        save_tasks(df)
        st.session_state["task_message"] = "🗑️ Task deleted"
        st.session_state["rerun_needed"] = True

    # ------------------- Initialize User File -------------------
    init_user_file()

    # ------------------- Sidebar -------------------
    st.sidebar.header(f"Welcome, {st.session_state['current_user']}")
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

    # ------------------- Display Task Messages -------------------
    if st.session_state.get("task_message"):
        st.info(st.session_state["task_message"])
        st.session_state["task_message"] = ""

    # ------------------- Motivational Quote -------------------
    st.markdown(
        f"""
        <div style="background-color:#2E86C1;padding:15px;border-radius:10px;margin-bottom:20px;">
            <h3 style="color:white;text-align:center;font-weight:600;font-size:20px;">{random.choice(quotes)}</h3>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ------------------- Safe rerun -------------------
    if st.session_state.get("rerun_needed"):
        st.session_state["rerun_needed"] = False
        st.experimental_rerun()

    # ------------------- Tabs -------------------
    tab1, tab2 = st.tabs(["📋 Task Board","📊 Analytics"])

    # ------------------- Task Board -------------------
    with tab1:
        df = get_tasks()
        if df.empty:
            st.info("No tasks yet. Add some from the sidebar!")
        else:
            status_order = ["To Do","In Progress","Done"]
            cols = st.columns(len(status_order))
            for idx, status in enumerate(status_order):
                with cols[idx]:
                    st.markdown(f"### {status}")
                    tasks = df[df["status"] == status]
                    for _, row in tasks.iterrows():
                        st.markdown(
                            f"""
                            <div style="background-color:{'#AED6F1' if status=='To Do' else '#F9E79F' if status=='In Progress' else '#ABEBC6'};
                                        padding:10px;border-radius:8px;margin-bottom:10px;">
                            <strong>{row['title']}</strong><br>
                            🔢 Priority: {row['priority']}<br>
                            🏷 Tag: {row['tag'] if row['tag'] else '-'}<br>
                            📅 Due: {row['due_date']}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        col1, col2 = st.columns([2,1])
                        with col1:
                            new_status = st.selectbox(
                                "Change Status",
                                options=status_order,
                                index=status_order.index(status),
                                key=f"status_{row['id']}"
                            )
                            if new_status != row['status']:
                                update_status(row['id'], new_status)
                        with col2:
                            if st.button("Delete", key=f"del_{row['id']}"):
                                delete_task(row['id'])

    # ------------------- Analytics -------------------
    with tab2:
        df = get_tasks()
        if df.empty:
            st.info("No tasks to analyze yet.")
        else:
            total = len(df)
            completed = len(df[df["status"]=="Done"])
            inprogress = len(df[df["status"]=="In Progress"])
            todo = len(df[df["status"]=="To Do"])
            avg_priority = df["priority"].mean() if not df.empty else 0

            st.subheader("Task Metrics")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Tasks", total)
            col2.metric("Completed", completed)
            col3.metric("In Progress", inprogress)
            col4.metric("Average Priority", f"{avg_priority:.2f}")

            st.subheader("Task Status Distribution")
            status_counts = df["status"].value_counts()
            fig1, ax1 = plt.subplots()
            ax1.pie(status_counts, labels=status_counts.index, autopct="%1.1f%%", startangle=90, colors=['#AED6F1','#F9E79F','#ABEBC6'])
            ax1.axis('equal')
            st.pyplot(fig1)

            st.subheader("Tasks Completed Over Time")
            if "completed_at" in df.columns:
                df["completed_at"] = pd.to_datetime(df["completed_at"], errors="coerce")
                df_completed = df.dropna(subset=["completed_at"])
                if not df_completed.empty:
                    df_line = df_completed.groupby(df_completed["completed_at"].dt.date).size()
                    st.line_chart(df_line)

            st.download_button(
                label="Download Tasks CSV",
                data=df.to_csv(index=False),
                file_name=f"tasks_{st.session_state['current_user']}.csv",
                mime="text/csv"
            )
