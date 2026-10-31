# 📚 Study Planner — Student Productivity & Task Manager

> A full-stack web application designed for students to organize study routines, automatically balance subject hours, and track daily academic tasks with complete user privacy.

![Python](https://img.shields.io/badge/Python-3.x-3776AB?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-000000?style=flat-square&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)
![HTML5](https://img.shields.io/badge/Frontend-HTML5%20%2F%20CSS3%20%2F%20JS-E34F26?style=flat-square&logo=html5&logoColor=white)

---

## 🌟 Key Features

- 🔐 **User Authentication & Data Privacy:**
  - Secure registration and login system with password hashing (`Werkzeug`).
  - **Complete Data Isolation:** Every user sees only their own tasks and study schedule.
  - Session-based access protection (`@login_required`).

- 🧠 **Smart Study Time Allocator:**
  - Balances your available daily study hours based on subject difficulty:
    - **Weak** $\rightarrow$ Highest priority & study time allocation.
    - **Medium** $\rightarrow$ Standard study duration.
    - **Strong** $\rightarrow$ Revision block.
  - Dynamically add or remove up to 6 curriculum subjects.

- 📝 **Task Management (CRUD):**
  - Create study tasks with subject, title, duration, time slot, priority, and due dates.
  - One-click task completion & reopening.
  - Safe task deletion with custom confirmation modals.
  - Real-time tab filters: *All*, *Pending*, *Completed*, *Overdue*, and *High Priority*.
  - Instant live search by title or subject without page reloads.

- 📊 **Dashboard & Progress Tracking:**
  - Real-time calculations: Total Tasks, Completion %, Pending Study Hours/Minutes.
  - Visual status alerts for overdue deadlines and tasks due today.

- 🎨 **Minimalist & Clean Theme System:**
  - **3 Color Themes:** Black (Dark), White (Light), and Purple.
  - Preferences persist across page reloads via browser `localStorage`.
  - Fully mobile-responsive layout with a clean collapsible sidebar.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Python, Flask |
| **Database & ORM** | SQLite, Flask-SQLAlchemy |
| **Authentication & Security** | Flask Session, Werkzeug Security (`scrypt` password hashing) |
| **Frontend** | HTML5, Modern CSS3 (Variables, Responsive Grid), Vanilla JavaScript |

---

## 📁 Project Structure

```text
smart-study-planner/
├── app.py                  # Application routes, database models, auth logic
├── ai_engine.py            # Subject weightage & study time allocation algorithm
├── requirements.txt        # Project dependencies
├── instance/
│   └── study_planner.db    # SQLite database (auto-created)
├── templates/
│   ├── login.html          # User sign-in page
│   ├── register.html       # User registration page
│   └── index.html          # Main student dashboard & workspace
└── static/
    ├── style.css           # Clean, responsive stylesheet with 3 theme modes
    └── app.js              # Client-side dynamic rows, filters, modals
```

---

## 🚀 Getting Started Locally

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/smart-study-planner.git
cd smart-study-planner
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the application
```bash
python app.py
```

### 4. Open in your browser
Navigate to:
```text
http://127.0.0.1:5000
```
- Create a new account via the **Register** link or sign in to start planning your studies.

---

## 👨‍💻 Author

**Pankaj Kharwar**
- Personal Full-Stack Project built with Python & Flask.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
