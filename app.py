import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
from datetime import datetime
import os
import threading
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

# ------------------- File Locking -------------------
file_locks = {}

def get_file_lock(filename):
    if filename not in file_locks:
        file_locks[filename] = threading.Lock()
    return file_locks[filename]

# ------------------- Page Config -------------------
if "page_config_done" not in st.session_state:
    st.set_page_config(
        page_title="Data Analyst To-Do List",
        page_icon="🧠",
        layout="centered"
    )
    st.session_state["page_config_done"] = True

# ------------------- Load Credentials YAML -------------------
with open('credentials.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config.get('preauthorized', [])
)

# ------------------- Session State -------------------
if "task_message" not in st.session_state:
    st.session_state["task_message"] = ""
if "rerun_needed" not in st.session_state:
    st.session_state["rerun_needed"] = False

# ------------------- Login -------------------
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Welcome {name}")

    # ------------------- User Task Functions -------------------
    def user_file():
        return f"tasks_{username}.csv"

    def init_user_file():
        f = user_file()
        lock = get_file_lock(f)
        with lock:
            if not os.path.exists(f):
                pd.DataFrame(columns=["id","title","status","priority","tag","due_date","created_at","completed_at"]).to_csv(f,index=False)

    def get_tasks():
        f = user_file()
        lock = get_file_lock(f)
        with lock:
            if os.path.exists(f):
                return pd.read_csv(f)
            else:
                return pd.DataFrame(columns=["id","title","status","priority","tag","due_date","created_at","completed_at"])

    def save_tasks(df):
        f = user_file()
        lock = get_file_lock(f)
        with lock:
            df.to_csv(f,index=False)

    def add_task(title, priority, tag, due_date):
        df = get_tasks()
        # Duplicate check across title, priority, due_date, and tag, case insensitive
        duplicate_cond = (
            (df["title"].str.lower() == title.lower()) &
            (df["priority"] == priority) &
            (df["due_date"] == due_date) &
            (df["tag"].str.lower().fillna("") == tag.lower())
        )
        if duplicate_cond.any():
            st.session_state["task_message"] = "⚠️ Task already exists with same name, priority, due date, and tag."
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

    # ------------------- Main App -------------------
    init_user_file()

    st.sidebar.header(f"Welcome, {name}")
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

    if st.session_state.get("task_message"):
        st.info(st.session_state["task_message"])
        st.session_state["task_message"] = ""

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

    if st.session_state.get("rerun_needed"):
        st.session_state["rerun_needed"] = False
        st.experimental_rerun()

    tab1, tab2 = st.tabs(["📋 Task Board","📊 Analytics"])

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
                        color_code = '#AED6F1' if status=='To Do' else '#F9E79F' if status=='In Progress' else '#ABEBC6'
                        st.markdown(
                            f"""
                            <div style="background-color:{color_code};
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
                file_name=f"tasks_{username}.csv",
                mime="text/csv"
            )

elif authentication_status is False:
    st.error("Username/password is incorrect")
else:
    st.warning("Please enter your username and password")
