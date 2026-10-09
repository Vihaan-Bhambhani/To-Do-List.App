# Task Manager & Productivity Analytics

A Python and Streamlit task-management app with a Kanban-style board, task-priority tracking, and descriptive analytics for completion patterns and estimated-versus-actual time.

## Features

### Task management
- Create tasks with a title, category, priority, due date, and estimated effort
- Organize tasks into **To Do**, **In Progress**, and **Done**
- Update task status and record actual time spent on completed tasks
- Delete tasks and flag overdue items
- Keep task records in per-user CSV files for a simple local prototype

### Descriptive analytics
- Total, completed, and in-progress task counts
- Completion rate and task-priority distribution
- Category breakdown
- Daily completion trend
- Estimated-versus-actual effort comparison
- Completion patterns by weekday
- CSV exports for task data and summary metrics

## Tech stack

- **Python**
- **Streamlit** — interactive application UI
- **pandas** — task data handling and aggregation
- **Plotly** — interactive charts
- **CSV** — lightweight local persistence

## Run locally

```bash
python -m venv .venv
```

Activate the environment:

**Windows**
```bash
.venv\Scripts\activate
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Install dependencies and start the app:

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Data model

Task records include:

| Field | Purpose |
|---|---|
| `id` | Task identifier |
| `title` | Task description |
| `status` | To Do, In Progress, or Done |
| `priority` | Priority level from 1 (highest) to 5 (lowest) |
| `tag` | Task category |
| `due_date` | Target completion date |
| `created_at` | Task creation timestamp |
| `completed_at` | Timestamp when task was marked Done |
| `estimated_hours` | Planned effort |
| `actual_hours` | User-entered effort for a completed task |

## Important scope and limitations

This is a **local portfolio prototype**, not a production multi-user service. Usernames and password hashes are stored in CSV files, and the current password hashing is not suitable for protecting real accounts. CSV files on a shared or hosted filesystem do not provide tenant isolation or durable storage. Do not use real or sensitive personal data in a public deployment.

The analytics are descriptive calculations over the tasks entered by the user. The project does **not** currently implement a genuine A/B-testing framework, statistical hypothesis testing, machine-learning predictions, or AI-generated insights. Completion rates and time comparisons should not be interpreted as evidence of productivity causation or as validated performance assessments.

---
**Author:** Vihaan Bhambhani
