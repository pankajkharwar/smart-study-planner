# StudyFlow — Student Study Planner

A full-stack study planning and task management application built with Python and Flask. StudyFlow helps students organize tasks, allocate study hours based on subject difficulty, and track academic progress.

## Features

- **User Authentication:** Registration and login with securely hashed passwords.
- **Data Privacy:** User-specific data access with protected routes and session management.
- **Smart Study Allocation:** Distributes daily study hours based on subject difficulty (Weak, Medium, Strong).
- **Task Management:** Create, update, complete, reopen, and delete study tasks.
- **Task Filters & Search:** Filter tasks by status, priority, and deadlines; search by title or subject.
- **Dashboard Analytics:** Track total tasks, completion progress, pending study time, and deadlines.
- **Theme Customization:** Dark, Light, and Purple themes with saved preferences.
- **Responsive Design:** Mobile-friendly layout with a collapsible sidebar.

## Tech Stack

| Layer | Technologies |
|---|---|
| Backend | Python, Flask |
| Database & ORM | SQLite, Flask-SQLAlchemy |
| Authentication | Flask Sessions, Werkzeug Security |
| Frontend | HTML5, CSS3, Vanilla JavaScript |

## Project Structure

```text
smart-study-planner/
├── app.py
├── ai_engine.py
├── requirements.txt
├── instance/
│   └── study_planner.db
├── templates/
│   ├── login.html
│   ├── register.html
│   └── index.html
└── static/
    ├── style.css
    └── app.js
```

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/pankajkharwar/YOUR_REPOSITORY_NAME.git
cd YOUR_REPOSITORY_NAME
```

Replace `YOUR_REPOSITORY_NAME` with your actual GitHub repository name.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
python app.py
```

### 4. Open in your browser

Visit:

```text
http://127.0.0.1:5000
```

Register an account or log in to start using StudyFlow.

## Author

**Pankaj Kharwar**

Developed as a personal full-stack project using Python and Flask.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
