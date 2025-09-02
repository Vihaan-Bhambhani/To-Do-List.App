# To-Do-List.App
# 🗂 To-Do List App (Data Analyst Demo)

A productivity-focused **To-Do List web app** built with **Streamlit**, designed not just for task management but also to demonstrate **data analysis, product analytics, and A/B testing skills**.  

This project was created as part of my Data Analyst internship application, showcasing how I think about **user behavior, product success metrics, and actionable insights**.

---

## 🚀 Features

- **Task Management**
  - Add tasks with **priority, category, and due dates**
  - Track status via **dropdown (To Do → In Progress → Done)**
  - Kanban board with **color-coded priorities**
  - Delete tasks safely

- **Motivational Quotes (A/B Testing)**
  - Built-in A/B experiment that assigns users to either:
    - 🎉 *Fun motivational quotes*  
    - 📈 *Professional productivity quotes*  
  - Demonstrates **experimentation design & tracking**

- **Analytics Dashboard**
  - Task completion progress bar
  - ⏱ Average completion time analysis
  - 📊 Tasks grouped by **priority** (SQL + bar chart)
  - 📂 Tasks grouped by **category** (SQL + bar chart)
  - 📅 Weekly completion trend (line chart)
  - SQL queries are displayed alongside results for **transparency**

- **Data-Driven UX**
  - 🎉 Balloons animation when a task is marked **Done**
  - Dark-themed motivational bar for readability
  - Insight messages highlighting trends (e.g., *“Most tasks are priority 3”*)

---

## 🛠️ Tech Stack

- **Python**
- **Streamlit** (frontend + backend in one)
- **SQLite** (persistent storage, schema migration included)
- **Pandas** (data wrangling & analysis)
- **Matplotlib** (visual analytics)

---

## 📈 Example SQL Queries Used

```sql
-- Tasks grouped by priority
SELECT priority, COUNT(*) FROM tasks GROUP BY priority;

-- Tasks grouped by category
SELECT tag, COUNT(*) FROM tasks GROUP BY tag;

