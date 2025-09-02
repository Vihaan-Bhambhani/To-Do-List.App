import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import random
from datetime import datetime, timedelta
import os
import hashlib
import numpy as np

# ------------------- Page Config -------------------
st.set_page_config(
    page_title="Data Analyst Portfolio - Task Management System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .task-card {
        border-left: 4px solid;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0 8px 8px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    .task-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    .priority-high { border-left-color: #e74c3c; background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); }
    .priority-medium { border-left-color: #f39c12; background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); }
    .priority-low { border-left-color: #27ae60; background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); }
    
    .sidebar-section {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .quote-container {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        text-align: center;
        color: white;
        font-weight: 600;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
    }
    .analytics-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-top: 4px solid #667eea;
    }
    .stSelectbox > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# ------------------- Session State -------------------
if "current_user" not in st.session_state:
    st.session_state["current_user"] = None
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "task_message" not in st.session_state:
    st.session_state["task_message"] = ""
if "tasks" not in st.session_state:
    st.session_state["tasks"] = pd.DataFrame()

# ------------------- Users CSV -------------------
USERS_FILE = "users.csv"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    try:
        if os.path.exists(USERS_FILE):
            df = pd.read_csv(USERS_FILE)
            if not all(col in df.columns for col in ["username", "password"]):
                df = pd.DataFrame(columns=["username","password"])
                df.to_csv(USERS_FILE, index=False)
            return df
        else:
            df = pd.DataFrame(columns=["username","password"])
            df.to_csv(USERS_FILE, index=False)
            return df
    except Exception as e:
        st.error(f"Error loading users: {e}")
        df = pd.DataFrame(columns=["username","password"])
        df.to_csv(USERS_FILE, index=False)
        return df

def save_users(df):
    try:
        df.to_csv(USERS_FILE, index=False)
    except Exception as e:
        st.error(f"Error saving users: {e}")

def user_exists(username):
    try:
        df = load_users()
        if df.empty:
            return False
        return username.lower() in df["username"].str.lower().values
    except Exception as e:
        st.error(f"Error checking user existence: {e}")
        return False

def validate_user(username, password):
    try:
        df = load_users()
        if df.empty:
            return "not_registered"
        matches = df[df["username"].str.lower() == username.lower()]
        if matches.empty:
            return "not_registered"
        elif matches.iloc[0]["password"] != hash_password(password):
            return "wrong_password"
        else:
            return "ok"
    except Exception as e:
        st.error(f"Error validating user: {e}")
        return "error"

# ------------------- Enhanced Motivational Quotes -------------------
quotes = [
    "🚀 Small steps every day lead to big results.",
    "🔥 Stay focused, the hard work will pay off.",
    "🌟 Progress, not perfection.",
    "💡 Every task you complete builds momentum.",
    "⏳ Don't wait for inspiration, create it.",
    "🏆 Winners are ordinary people with extraordinary consistency.",
    "🎯 Focus on what matters most today.",
    "⚡ You've got this - one task at a time.",
    "📈 Small wins lead to big victories.",
    "🎊 Celebrate progress, no matter how small.",
    "✨ Make it happen, step by step.",
    "🌈 Every completed task is a step forward.",
]

# ------------------- Login/Register -------------------
def login_register():
    st.markdown("""
    <div class="main-header">
        <h1>📊 Data Analyst Portfolio</h1>
        <h3>Advanced Task Management & Analytics System</h3>
        <p>Demonstrating data-driven productivity and visualization skills</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🔐 Access Portal")
        action = st.radio("Choose Action:", ["Login", "Register"], horizontal=True)
        
        with st.form("login_form"):
            username = st.text_input("👤 Username", placeholder="Enter your username")
            password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
            confirm_password = ""
            if action == "Register":
                confirm_password = st.text_input("🔑 Confirm Password", type="password", placeholder="Confirm your password")
            submitted = st.form_submit_button("🚀 " + action, use_container_width=True)
            
            if submitted:
                if not username.strip() or not password:
                    st.warning("⚠️ Please enter both username and password.")
                    return False
                elif action == "Register" and password != confirm_password:
                    st.warning("⚠️ Passwords do not match.")
                    return False
                elif action == "Register" and user_exists(username):
                    st.warning("⚠️ Username already exists.")
                    return False
                elif action == "Register":
                    try:
                        df = load_users()
                        new_user = pd.DataFrame([{"username": username.lower(), "password": hash_password(password)}])
                        df = pd.concat([df, new_user], ignore_index=True)
                        save_users(df)
                        st.session_state["current_user"] = username.lower()
                        st.session_state["logged_in"] = True
                        st.success(f"🎉 Welcome {username}! Registration successful!")
                        st.rerun()
                        return True
                    except Exception as e:
                        st.error(f"Registration error: {e}")
                        return False
                elif action == "Login":
                    result = validate_user(username, password)
                    if result == "not_registered":
                        st.warning("⚠️ Username not found. Please register first.")
                        return False
                    elif result == "wrong_password":
                        st.warning("⚠️ Incorrect password.")
                        return False
                    elif result == "error":
                        st.error("⚠️ Login error. Please try again.")
                        return False
                    else:
                        st.session_state["current_user"] = username.lower()
                        st.session_state["logged_in"] = True
                        st.success(f"🎊 Welcome back, {username}!")
                        st.rerun()
                        return True
    return False

if not st.session_state["logged_in"]:
    logged_in_now = login_register()
    if not logged_in_now:
        st.stop()

# ------------------- Task Storage -------------------
def user_file():
    return f"tasks_{st.session_state['current_user']}.csv"

def init_user_file():
    try:
        f = user_file()
        if not os.path.exists(f):
            df = pd.DataFrame(columns=["id","title","status","priority","tag","due_date","created_at","completed_at","estimated_hours","actual_hours"])
            df.to_csv(f, index=False)
    except Exception as e:
        st.error(f"Error initializing user file: {e}")

def load_tasks():
    try:
        f = user_file()
        if os.path.exists(f):
            df = pd.read_csv(f)
            required_columns = ["id","title","status","priority","tag","due_date","created_at","completed_at","estimated_hours","actual_hours"]
            for col in required_columns:
                if col not in df.columns:
                    df[col] = "" if col not in ["estimated_hours", "actual_hours"] else 0
        else:
            df = pd.DataFrame(columns=["id","title","status","priority","tag","due_date","created_at","completed_at","estimated_hours","actual_hours"])
        st.session_state["tasks"] = df
    except Exception as e:
        st.error(f"Error loading tasks: {e}")
        st.session_state["tasks"] = pd.DataFrame(columns=["id","title","status","priority","tag","due_date","created_at","completed_at","estimated_hours","actual_hours"])

def save_tasks():
    try:
        st.session_state["tasks"].to_csv(user_file(), index=False)
    except Exception as e:
        st.error(f"Error saving tasks: {e}")

init_user_file()
load_tasks()

# ------------------- Main Header (Only show before login) -------------------
# This section is now moved to after login check

# ------------------- Sidebar: Enhanced Task Creation -------------------
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-section" style="text-align: center; color: white;">
        <h3>👋 Welcome, {st.session_state['current_user'].title()}</h3>
        <p>Data-Driven Productivity</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### ➕ Create New Task")
    
    with st.form("task_form"):
        title = st.text_input("📝 Task Title", placeholder="Enter task description...")
        
        col1, col2 = st.columns(2)
        with col1:
            priority = st.selectbox("🎯 Priority", [1,2,3,4,5], 
                                  format_func=lambda x: f"🔴 Critical" if x==1 else f"🟡 High" if x==2 else f"🟢 Medium" if x==3 else f"🔵 Low" if x==4 else "⚫ Minimal")
        with col2:
            estimated_hours = st.number_input("⏱️ Est. Hours", min_value=0.5, max_value=40.0, step=0.5, value=1.0)
            
        tag = st.selectbox("🏷️ Category", 
                          ["Data Analysis", "Visualization", "Research", "Reporting", "Learning", "Meeting", "Other"])
        due_date = st.date_input("📅 Due Date", min_value=datetime.now().date())
        
        submitted = st.form_submit_button("🚀 Add Task", use_container_width=True)
        
        if submitted:
            if title.strip():
                try:
                    df = st.session_state["tasks"]
                    if not df.empty and len(df) > 0:
                        duplicate_check = ((df["title"].str.lower() == title.lower()) & (df["priority"] == priority)).any()
                    else:
                        duplicate_check = False
                        
                    if duplicate_check:
                        st.warning("⚠️ Similar task already exists!")
                    else:
                        task_id = str(datetime.now().timestamp()).replace(".", "")
                        new_task = {
                            "id": task_id,
                            "title": title,
                            "status": "To Do",
                            "priority": priority,
                            "tag": tag,
                            "due_date": str(due_date),
                            "created_at": datetime.now().isoformat(),
                            "completed_at": "",
                            "estimated_hours": estimated_hours,
                            "actual_hours": 0
                        }
                        new_task_df = pd.DataFrame([new_task])
                        st.session_state["tasks"] = pd.concat([df, new_task_df], ignore_index=True)
                        save_tasks()
                        st.success("✅ Task created successfully!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error adding task: {e}")
            else:
                st.warning("⚠️ Please enter a task title.")
    
    # Quick Stats in Sidebar
    if not st.session_state["tasks"].empty:
        df = st.session_state["tasks"]
        st.markdown("### 📈 Quick Stats")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📋 Total", len(df))
            st.metric("✅ Done", len(df[df["status"]=="Done"]))
        with col2:
            completion_rate = len(df[df["status"]=="Done"]) / len(df) * 100 if len(df) > 0 else 0
            st.metric("🎯 Rate", f"{completion_rate:.0f}%")
            st.metric("⚡ Active", len(df[df["status"]!="Done"]))
    
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state["logged_in"] = False
        st.session_state["current_user"] = None
        st.session_state["tasks"] = pd.DataFrame()
        st.rerun()

# ------------------- Motivational Quote (Visible after login) -------------------
st.markdown(f"""
<div class="quote-container">
    <h3>{random.choice(quotes)}</h3>
</div>
""", unsafe_allow_html=True)

# ------------------- Enhanced Tabs -------------------
tab1, tab2, tab3 = st.tabs(["📋 Kanban Board", "📊 Analytics Dashboard", "📈 Performance Insights"])

# ------------------- Enhanced Task Board -------------------
status_order = ["To Do", "In Progress", "Done"]
status_colors = {"To Do": "#3498db", "In Progress": "#f39c12", "Done": "#27ae60"}
status_emojis = {"To Do": "📝", "In Progress": "⚡", "Done": "✅"}

with tab1:
    try:
        df = st.session_state["tasks"]
        if df.empty:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white;">
                <h2>✨ Time to get things done!</h2>
                <p>Add your first task from the sidebar and start building momentum.</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Task board columns
            cols = st.columns(len(status_order))
            for idx, status in enumerate(status_order):
                with cols[idx]:
                    tasks_count = len(df[df["status"] == status])
                    st.markdown(f"""
                    <div style="background: {status_colors[status]}; color: white; padding: 1rem; border-radius: 10px; text-align: center; margin-bottom: 1rem;">
                        <h3>{status_emojis[status]} {status}</h3>
                        <p>{tasks_count} tasks</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    tasks = df[df["status"] == status].sort_values("priority")
                    for _, row in tasks.iterrows():
                        try:
                            # Priority styling
                            priority_class = "priority-high" if row['priority'] <= 2 else "priority-medium" if row['priority'] <= 3 else "priority-low"
                            priority_emoji = "🔴" if row['priority'] == 1 else "🟡" if row['priority'] == 2 else "🟢" if row['priority'] == 3 else "🔵" if row['priority'] == 4 else "⚫"
                            
                            task_tag = row['tag'] if pd.notna(row['tag']) and row['tag'] else 'General'
                            task_due = row['due_date'] if pd.notna(row['due_date']) else 'No date'
                            est_hours = row['estimated_hours'] if pd.notna(row['estimated_hours']) else 0
                            
                            # Days until due
                            try:
                                due_date_obj = datetime.strptime(task_due, '%Y-%m-%d').date()
                                days_left = (due_date_obj - datetime.now().date()).days
                                urgency_color = "#e74c3c" if days_left < 0 else "#f39c12" if days_left < 3 else "#27ae60"
                                urgency_text = f"⚠️ {abs(days_left)} days overdue" if days_left < 0 else f"🔥 {days_left} days left" if days_left < 3 else f"📅 {days_left} days left"
                            except:
                                urgency_color = "#95a5a6"
                                urgency_text = "📅 No due date"
                            
                            st.markdown(f"""
                            <div class="task-card {priority_class}">
                                <h4 style="margin: 0; color: #2c3e50;">{row['title']}</h4>
                                <div style="margin: 0.5rem 0;">
                                    <span style="background: #34495e; color: white; padding: 0.2rem 0.5rem; border-radius: 15px; font-size: 0.8rem; margin-right: 0.5rem;">
                                        {priority_emoji} P{row['priority']}
                                    </span>
                                    <span style="background: #3498db; color: white; padding: 0.2rem 0.5rem; border-radius: 15px; font-size: 0.8rem; margin-right: 0.5rem;">
                                        🏷️ {task_tag}
                                    </span>
                                    <span style="background: #9b59b6; color: white; padding: 0.2rem 0.5rem; border-radius: 15px; font-size: 0.8rem;">
                                        ⏱️ {est_hours}h
                                    </span>
                                </div>
                                <div style="color: {urgency_color}; font-weight: 600; font-size: 0.9rem;">
                                    {urgency_text}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Enhanced controls
                            col1, col2, col3 = st.columns([2, 1, 1])
                            with col1:
                                current_status = row["status"] if row["status"] in status_order else "To Do"
                                new_status = st.selectbox(
                                    "Status",
                                    options=status_order,
                                    index=status_order.index(current_status),
                                    key=f"status_{row['id']}",
                                    label_visibility="collapsed"
                                )
                                if new_status != current_status:
                                    st.session_state["tasks"].loc[df["id"]==row["id"], "status"] = new_status
                                    if new_status == "Done":
                                        st.session_state["tasks"].loc[df["id"]==row["id"], "completed_at"] = datetime.now().isoformat()
                                        # Auto-set actual hours to estimated if not already set
                                        if pd.isna(row['actual_hours']) or row['actual_hours'] == 0:
                                            st.session_state["tasks"].loc[df["id"]==row["id"], "actual_hours"] = est_hours
                                    save_tasks()
                                    st.rerun()
                            
                            with col2:
                                if row["status"] == "Done":
                                    actual_hours = st.number_input(
                                        "Actual Hours",
                                        min_value=0.1,
                                        max_value=50.0,
                                        value=float(row['actual_hours']) if pd.notna(row['actual_hours']) and row['actual_hours'] > 0 else est_hours,
                                        step=0.1,
                                        key=f"hours_{row['id']}",
                                        label_visibility="collapsed"
                                    )
                                    if actual_hours != row['actual_hours']:
                                        st.session_state["tasks"].loc[df["id"]==row["id"], "actual_hours"] = actual_hours
                                        save_tasks()
                                        st.rerun()
                            
                            with col3:
                                if st.button("🗑️", key=f"del_{row['id']}", help="Delete task"):
                                    st.session_state["tasks"] = df[df["id"] != row["id"]].reset_index(drop=True)
                                    save_tasks()
                                    st.success("🗑️ Task deleted")
                                    st.rerun()
                                    
                            st.markdown("---")
                            
                        except Exception as e:
                            st.error(f"Error displaying task: {e}")
    except Exception as e:
        st.error(f"Error in task board: {e}")

# ------------------- Enhanced Analytics -------------------
with tab2:
    try:
        df = st.session_state["tasks"]
        if df.empty:
            st.info("📊 Create some tasks to see powerful analytics in action!")
        else:
            # Key Metrics Row
            col1, col2, col3, col4, col5 = st.columns(5)
            
            total_tasks = len(df)
            completed_tasks = len(df[df["status"]=="Done"])
            in_progress = len(df[df["status"]=="In Progress"])
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            avg_priority = df["priority"].mean() if not df.empty else 0
            
            with col1:
                st.markdown(f"""
                <div class="metric-container">
                    <h2>📋</h2>
                    <h3>{total_tasks}</h3>
                    <p>Total Tasks</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-container">
                    <h2>✅</h2>
                    <h3>{completed_tasks}</h3>
                    <p>Completed</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-container">
                    <h2>⚡</h2>
                    <h3>{in_progress}</h3>
                    <p>In Progress</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-container">
                    <h2>🎯</h2>
                    <h3>{completion_rate:.0f}%</h3>
                    <p>Completion Rate</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col5:
                st.markdown(f"""
                <div class="metric-container">
                    <h2>⭐</h2>
                    <h3>{avg_priority:.1f}</h3>
                    <p>Avg Priority</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Interactive Charts Row
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
                st.subheader("📊 Task Distribution by Status")
                
                status_counts = df["status"].value_counts()
                fig_pie = px.pie(
                    values=status_counts.values,
                    names=status_counts.index,
                    color_discrete_map=status_colors,
                    title="Task Status Distribution"
                )
                fig_pie.update_traces(textposition='inside', textinfo='percent+label')
                fig_pie.update_layout(height=400, showlegend=True)
                st.plotly_chart(fig_pie, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
                st.subheader("🎯 Priority Analysis")
                
                priority_counts = df["priority"].value_counts().sort_index()
                priority_labels = {1: "Critical", 2: "High", 3: "Medium", 4: "Low", 5: "Minimal"}
                
                fig_bar = px.bar(
                    x=[priority_labels[p] for p in priority_counts.index],
                    y=priority_counts.values,
                    color=priority_counts.values,
                    color_continuous_scale="RdYlGn_r",
                    title="Tasks by Priority Level"
                )
                fig_bar.update_layout(height=400, xaxis_title="Priority", yaxis_title="Number of Tasks")
                st.plotly_chart(fig_bar, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Category Analysis
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
                st.subheader("🏷️ Category Breakdown")
                
                category_counts = df["tag"].value_counts()
                fig_donut = px.pie(
                    values=category_counts.values,
                    names=category_counts.index,
                    title="Tasks by Category",
                    hole=0.4
                )
                fig_donut.update_traces(textposition='inside', textinfo='percent+label')
                fig_donut.update_layout(height=400)
                st.plotly_chart(fig_donut, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
                st.subheader("📈 Completion Trend")
                
                try:
                    df_copy = df.copy()
                    df_copy["completed_at"] = pd.to_datetime(df_copy["completed_at"], errors="coerce")
                    df_completed = df_copy.dropna(subset=["completed_at"])
                    
                    if not df_completed.empty:
                        df_completed['completion_date'] = df_completed["completed_at"].dt.date
                        daily_completions = df_completed.groupby('completion_date').size().reset_index(name='completed_tasks')
                        
                        fig_line = px.line(
                            daily_completions,
                            x='completion_date',
                            y='completed_tasks',
                            title='Daily Task Completions',
                            markers=True
                        )
                        fig_line.update_layout(height=400, xaxis_title="Date", yaxis_title="Tasks Completed")
                        st.plotly_chart(fig_line, use_container_width=True)
                    else:
                        st.info("Complete some tasks to see the trend!")
                except Exception as e:
                    st.error(f"Error creating completion chart: {e}")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"Error in analytics: {e}")

# ------------------- Performance Insights -------------------
with tab3:
    try:
        df = st.session_state["tasks"]
        if df.empty:
            st.info("📈 Complete some tasks to unlock performance insights!")
        else:
            st.subheader("🎯 Performance Dashboard")
            
            # Time management analysis
            completed_df = df[df["status"] == "Done"].copy()
            
            if not completed_df.empty:
                # Time estimation accuracy
                completed_df["estimated_hours"] = pd.to_numeric(completed_df["estimated_hours"], errors="coerce").fillna(0)
                completed_df["actual_hours"] = pd.to_numeric(completed_df["actual_hours"], errors="coerce").fillna(0)
                
                valid_time_data = completed_df[(completed_df["estimated_hours"] > 0) & (completed_df["actual_hours"] > 0)]
                
                if not valid_time_data.empty:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
                        st.subheader("⏱️ Time Estimation Accuracy")
                        
                        accuracy_data = []
                        for _, row in valid_time_data.iterrows():
                            accuracy = (min(row["estimated_hours"], row["actual_hours"]) / max(row["estimated_hours"], row["actual_hours"])) * 100
                            accuracy_data.append({
                                "Task": row["title"][:20] + "..." if len(row["title"]) > 20 else row["title"],
                                "Estimated": row["estimated_hours"],
                                "Actual": row["actual_hours"],
                                "Accuracy": accuracy
                            })
                        
                        if accuracy_data:
                            accuracy_df = pd.DataFrame(accuracy_data)
                            avg_accuracy = accuracy_df["Accuracy"].mean()
                            
                            fig_accuracy = px.scatter(
                                accuracy_df,
                                x="Estimated",
                                y="Actual",
                                hover_data=["Task", "Accuracy"],
                                title=f"Estimation vs Actual Time (Avg Accuracy: {avg_accuracy:.1f}%)",
                                color="Accuracy",
                                color_continuous_scale="RdYlGn"
                            )
                            # Add perfect estimation line
                            max_hours = max(accuracy_df["Estimated"].max(), accuracy_df["Actual"].max())
                            fig_accuracy.add_shape(
                                type="line",
                                x0=0, y0=0, x1=max_hours, y1=max_hours,
                                line=dict(color="gray", dash="dash"),
                            )
                            fig_accuracy.update_layout(height=400)
                            st.plotly_chart(fig_accuracy, use_container_width=True)
                        
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
                        st.subheader("📊 Productivity Metrics")
                        
                        # Calculate productivity metrics
                        total_estimated = valid_time_data["estimated_hours"].sum()
                        total_actual = valid_time_data["actual_hours"].sum()
                        efficiency = (total_estimated / total_actual * 100) if total_actual > 0 else 100
                        
                        # Create gauge chart for efficiency
                        fig_gauge = go.Figure(go.Indicator(
                            mode = "gauge+number+delta",
                            value = efficiency,
                            domain = {'x': [0, 1], 'y': [0, 1]},
                            title = {'text': "Time Efficiency %"},
                            delta = {'reference': 100},
                            gauge = {
                                'axis': {'range': [None, 150]},
                                'bar': {'color': "darkblue"},
                                'steps': [
                                    {'range': [0, 50], 'color': "lightgray"},
                                    {'range': [50, 80], 'color': "yellow"},
                                    {'range': [80, 100], 'color': "lightgreen"},
                                    {'range': [100, 150], 'color': "green"}
                                ],
                                'threshold': {
                                    'line': {'color': "red", 'width': 4},
                                    'thickness': 0.75,
                                    'value': 100
                                }
                            }
                        ))
                        fig_gauge.update_layout(height=400)
                        st.plotly_chart(fig_gauge, use_container_width=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                
                # Task completion pattern analysis
                st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
                st.subheader("📅 Weekly Performance Pattern")
                
                try:
                    completed_df["completed_at"] = pd.to_datetime(completed_df["completed_at"], errors="coerce")
                    if not completed_df.empty:
                        completed_df["weekday"] = completed_df["completed_at"].dt.day_name()
                        completed_df["hour"] = completed_df["completed_at"].dt.hour
                        
                        # Weekday analysis
                        weekday_counts = completed_df["weekday"].value_counts()
                        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                        weekday_counts = weekday_counts.reindex(weekday_order, fill_value=0)
                        
                        fig_weekday = px.bar(
                            x=weekday_counts.index,
                            y=weekday_counts.values,
                            title="Tasks Completed by Day of Week",
                            color=weekday_counts.values,
                            color_continuous_scale="viridis"
                        )
                        fig_weekday.update_layout(xaxis_title="Day", yaxis_title="Tasks Completed")
                        st.plotly_chart(fig_weekday, use_container_width=True)
                except Exception as e:
                    st.info("Complete more tasks to see weekly patterns!")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            else:
                st.info("💡 Complete some tasks to unlock detailed performance insights!")
            
            # Advanced Analytics Summary
            st.markdown('<div class="analytics-card">', unsafe_allow_html=True)
            st.subheader("🧠 Data Analyst Insights")
            
            insights = []
            
            # Completion rate insight
            if completion_rate > 80:
                insights.append("🎯 **Excellent completion rate!** You demonstrate strong follow-through on commitments.")
            elif completion_rate > 60:
                insights.append("📈 **Good completion rate.** Consider strategies to boost task completion.")
            else:
                insights.append("🔍 **Opportunity for improvement** in task completion rates.")
            
            # Priority management insight
            high_priority_completed = len(df[(df["priority"] <= 2) & (df["status"] == "Done")])
            high_priority_total = len(df[df["priority"] <= 2])
            if high_priority_total > 0:
                high_priority_rate = high_priority_completed / high_priority_total * 100
                if high_priority_rate > 80:
                    insights.append("🚀 **Strong priority management** - you focus on high-impact tasks.")
                else:
                    insights.append("⚠️ **Focus on high-priority tasks** to maximize impact.")
            
            # Category analysis insight
            if not df.empty:
                most_common_category = df["tag"].mode().iloc[0] if not df["tag"].mode().empty else "General"
                insights.append(f"📊 **Primary focus area:** {most_common_category} - shows specialization depth.")
            
            # Time management insight
            if not completed_df.empty and not valid_time_data.empty:
                avg_efficiency = valid_time_data.apply(lambda row: min(row["estimated_hours"], row["actual_hours"]) / max(row["estimated_hours"], row["actual_hours"]) * 100, axis=1).mean()
                if avg_efficiency > 80:
                    insights.append("⏱️ **Excellent time estimation skills** - crucial for project planning.")
                else:
                    insights.append("📊 **Developing time estimation abilities** - valuable analytical skill.")
            
            for insight in insights:
                st.markdown(insight)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Export options
            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button(
                    label="📥 Download Full Dataset",
                    data=df.to_csv(index=False),
                    file_name=f"task_analytics_{st.session_state['current_user']}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            
            with col2:
                if not completed_df.empty:
                    completed_summary = completed_df.groupby("tag").agg({
                        "id": "count",
                        "estimated_hours": "sum",
                        "actual_hours": "sum"
                    }).rename(columns={"id": "completed_tasks"})
                    
                    st.download_button(
                        label="📊 Download Summary Report",
                        data=completed_summary.to_csv(),
                        file_name=f"productivity_report_{st.session_state['current_user']}_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            with col3:
                # Create a performance report
                performance_data = {
                    "Metric": ["Total Tasks", "Completion Rate", "Avg Priority", "Categories Used", "Avg Estimation Accuracy"],
                    "Value": [
                        total_tasks,
                        f"{completion_rate:.1f}%",
                        f"{avg_priority:.1f}",
                        df["tag"].nunique(),
                        f"{avg_efficiency:.1f}%" if not completed_df.empty and not valid_time_data.empty else "N/A"
                    ]
                }
                performance_df = pd.DataFrame(performance_data)
                
                st.download_button(
                    label="📈 Download Performance KPIs",
                    data=performance_df.to_csv(index=False),
                    file_name=f"kpi_dashboard_{st.session_state['current_user']}_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
    except Exception as e:
        st.error(f"Error in performance insights: {e}")

# ------------------- Footer -------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white; margin-top: 2rem;">
    <h4>📊 Data Analyst Portfolio Project</h4>
    <p>Demonstrating: Python • Streamlit • Data Visualization • User Experience Design • System Architecture</p>
    <p><em>Built to showcase analytical thinking and technical implementation skills</em></p>
</div>
""", unsafe_allow_html=True)
