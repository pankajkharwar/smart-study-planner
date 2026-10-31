import os
from datetime import date
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text
from werkzeug.security import generate_password_hash, check_password_hash
from ai_engine import generate_study_plan

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "study-planner-pankaj-secure-key-2026")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///study_planner.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

MAX_SUBJECTS = 6
ALLOWED_DIFFICULTIES = {"weak", "medium", "strong"}
ALLOWED_TIME_SLOTS = {"Morning", "Afternoon", "Evening", "Flexible"}
ALLOWED_PRIORITIES = {"Low", "Medium", "High"}


# --------------------------------------------------------------------------
# DATABASE MODELS
# --------------------------------------------------------------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    fullname = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.Date, default=date.today)

    tasks = db.relationship("StudyTask", backref="user", lazy=True, cascade="all, delete-orphan")


class StudyTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    student_name = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(80), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    time_slot = db.Column(db.String(20), nullable=False, default="Flexible")
    completed = db.Column(db.Boolean, nullable=False, default=False)
    due_date = db.Column(db.Date, nullable=True)
    priority = db.Column(db.String(10), nullable=False, default="Medium")

    @property
    def status_category(self):
        """Helper to classify task timeline category."""
        if self.completed:
            return "completed"
        if not self.due_date:
            return "no_deadline"
        today = date.today()
        if self.due_date < today:
            return "overdue"
        elif self.due_date == today:
            return "due_today"
        else:
            return "upcoming"


# --------------------------------------------------------------------------
# AUTH HELPER / DECORATOR
# --------------------------------------------------------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Please sign in to access your study planner.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# --------------------------------------------------------------------------
# AUTH ROUTES (REGISTER, LOGIN, LOGOUT)
# --------------------------------------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")

        if not fullname or len(fullname) > 80:
            flash("Please enter a valid full name (max 80 chars).", "error")
            return render_template("register.html")

        if not username or len(username) < 3 or len(username) > 50:
            flash("Username must be between 3 and 50 characters.", "error")
            return render_template("register.html")

        if not password or len(password) < 4:
            flash("Password must be at least 4 characters.", "error")
            return render_template("register.html")

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already taken. Please choose another.", "error")
            return render_template("register.html")

        # First registered user or username "pankaj" gets admin rights
        is_first = User.query.count() == 0 or username == "pankaj"

        new_user = User(
            fullname=fullname,
            username=username,
            password_hash=generate_password_hash(password),
            is_admin=is_first
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Account created successfully! Please sign in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid username or password.", "error")
            return render_template("login.html")

        # Session login
        session["user_id"] = user.id
        session["username"] = user.username
        session["fullname"] = user.fullname
        session["is_admin"] = user.is_admin

        flash(f"Welcome back, {user.fullname}!", "success")
        return redirect(url_for("home"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("login"))


# --------------------------------------------------------------------------
# MAIN DASHBOARD ROUTE (PROTECTED)
# --------------------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    current_user_id = session.get("user_id")
    current_user_name = session.get("fullname", "Student")
    is_admin = session.get("is_admin", False)

    plan = None
    errors = []
    student_name = current_user_name
    daily_hours = ""
    preferred_time = "Flexible"
    subject_rows = [{"name": "", "difficulty": "weak"}]

    if request.method == "POST":
        student_name = request.form.get("student_name", "").strip() or current_user_name
        daily_hours = request.form.get("hours", "").strip()
        preferred_time = request.form.get("preferred_time", "Flexible")

        subject_names = request.form.getlist("subject_name")
        difficulties = request.form.getlist("difficulty")

        if not student_name or len(student_name) > 80:
            errors.append("Student name must be between 1 and 80 characters.")

        if preferred_time not in ALLOWED_TIME_SLOTS:
            errors.append("Please select a valid preferred study time slot.")

        if not 1 <= len(subject_names) <= MAX_SUBJECTS:
            errors.append(f"Please add between 1 and {MAX_SUBJECTS} subjects.")

        if len(subject_names) != len(difficulties):
            errors.append("Subject details are incomplete or mismatched.")

        subject_rows = [
            {"name": name.strip(), "difficulty": difficulty.lower().strip()}
            for name, difficulty in zip(subject_names, difficulties)
        ]

        subjects = []
        seen_names = set()

        for subject in subject_rows:
            name = subject["name"]
            difficulty = subject["difficulty"]

            if not name:
                errors.append("Every subject must have a valid name.")
                continue

            if len(name) > 80:
                errors.append(f"Subject '{name[:20]}...' exceeds 80 characters.")
                continue

            if name.casefold() in seen_names:
                errors.append(f"Duplicate subject name detected: '{name}'.")
                continue

            seen_names.add(name.casefold())

            if difficulty not in ALLOWED_DIFFICULTIES:
                errors.append(f"Invalid difficulty for subject: '{name}'.")
                continue

            subjects.append({
                "name": name,
                "difficulty": difficulty
            })

        try:
            hours_value = float(daily_hours)
            if not 0 < hours_value <= 24:
                errors.append("Study hours must be greater than 0 and at most 24.")
        except (ValueError, TypeError):
            hours_value = 0
            errors.append("Please enter valid numerical study hours (e.g., 2, 4.5).")

        if not errors:
            plan = generate_study_plan(subjects, hours_value)

    # USER PRIVACY: Fetch ONLY this user's tasks
    # (If admin Pankaj, you can see all or own, but here every user sees only their own tasks cleanly)
    tasks = StudyTask.query.filter_by(user_id=current_user_id).order_by(StudyTask.completed.asc(), StudyTask.id.desc()).all()
    today = date.today()

    total_tasks = len(tasks)
    completed_count = sum(1 for task in tasks if task.completed)
    pending_count = total_tasks - completed_count
    completion_rate = int(round((completed_count * 100 / total_tasks))) if total_tasks > 0 else 0

    overdue_tasks = [t for t in tasks if t.due_date and t.due_date < today and not t.completed]
    due_today_tasks = [t for t in tasks if t.due_date and t.due_date == today and not t.completed]
    upcoming_tasks = [t for t in tasks if t.due_date and t.due_date > today and not t.completed]
    high_priority_count = sum(1 for t in tasks if t.priority == "High" and not t.completed)
    pending_minutes = sum(t.duration_minutes for t in tasks if not t.completed)

    return render_template(
        "index.html",
        plan=plan,
        errors=errors,
        student_name=student_name,
        daily_hours=daily_hours,
        preferred_time=preferred_time,
        subject_rows=subject_rows,
        tasks=tasks,
        today=today,
        total_tasks=total_tasks,
        completed_count=completed_count,
        pending_count=pending_count,
        completion_rate=completion_rate,
        overdue_tasks=overdue_tasks,
        overdue_count=len(overdue_tasks),
        due_today_tasks=due_today_tasks,
        due_today_count=len(due_today_tasks),
        upcoming_tasks=upcoming_tasks,
        upcoming_count=len(upcoming_tasks),
        high_priority_count=high_priority_count,
        pending_minutes=pending_minutes,
        pending_hours=round(pending_minutes / 60, 1),
        current_user_name=current_user_name,
        is_admin=is_admin
    )


# --------------------------------------------------------------------------
# TASK ACTIONS (PROTECTED PER USER)
# --------------------------------------------------------------------------
@app.route("/tasks/add", methods=["POST"])
@login_required
def add_task():
    current_user_id = session.get("user_id")
    student_name = session.get("fullname", request.form.get("student_name", "").strip())
    title = request.form.get("title", "").strip()
    subject = request.form.get("subject", "").strip()
    duration = request.form.get("duration", "").strip()
    time_slot = request.form.get("time_slot", "Flexible").strip()
    due_date_input = request.form.get("due_date", "").strip()
    priority = request.form.get("priority", "Medium").strip().title()

    if not title or len(title) > 200:
        flash("Task title must be between 1 and 200 characters.", "error")
        return redirect(url_for("home") + "#add-task")

    if not subject or len(subject) > 80:
        flash("Subject name must be between 1 and 80 characters.", "error")
        return redirect(url_for("home") + "#add-task")

    if time_slot not in ALLOWED_TIME_SLOTS:
        flash("Please select a valid time slot.", "error")
        return redirect(url_for("home") + "#add-task")

    if priority not in ALLOWED_PRIORITIES:
        flash("Please select a valid priority (Low, Medium, or High).", "error")
        return redirect(url_for("home") + "#add-task")

    try:
        duration_minutes = int(duration)
        if not 1 <= duration_minutes <= 1440:
            flash("Task duration must be between 1 and 1440 minutes.", "error")
            return redirect(url_for("home") + "#add-task")
    except (ValueError, TypeError):
        flash("Please enter a valid numeric task duration in minutes.", "error")
        return redirect(url_for("home") + "#add-task")

    parsed_due_date = None
    if due_date_input:
        try:
            parsed_due_date = date.fromisoformat(due_date_input)
        except ValueError:
            flash("Please enter a valid due date (YYYY-MM-DD).", "error")
            return redirect(url_for("home") + "#add-task")

    task = StudyTask(
        user_id=current_user_id,
        student_name=student_name,
        title=title,
        subject=subject,
        duration_minutes=duration_minutes,
        time_slot=time_slot,
        due_date=parsed_due_date,
        priority=priority,
        completed=False
    )

    db.session.add(task)
    db.session.commit()
    flash(f"Task '{title}' created successfully!", "success")

    return redirect(url_for("home") + "#tasks")


@app.route("/tasks/<int:task_id>/toggle", methods=["POST"])
@login_required
def toggle_task(task_id):
    current_user_id = session.get("user_id")
    # Only allow toggling own tasks
    task = StudyTask.query.filter_by(id=task_id, user_id=current_user_id).first_or_404()
    task.completed = not task.completed
    db.session.commit()
    status_msg = "marked as completed" if task.completed else "reopened"
    flash(f"Task '{task.title}' {status_msg}.", "info")

    return redirect(url_for("home") + "#tasks")


@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def delete_task(task_id):
    current_user_id = session.get("user_id")
    # Only allow deleting own tasks
    task = StudyTask.query.filter_by(id=task_id, user_id=current_user_id).first_or_404()
    title = task.title
    db.session.delete(task)
    db.session.commit()
    flash(f"Task '{title}' has been deleted.", "warning")

    return redirect(url_for("home") + "#tasks")


# --------------------------------------------------------------------------
# DATABASE MIGRATION & INIT
# --------------------------------------------------------------------------
with app.app_context():
    db.create_all()

    inspector = inspect(db.engine)
    columns = {
        column["name"]
        for column in inspector.get_columns("study_task")
    }

    with db.engine.begin() as connection:
        if "user_id" not in columns:
            connection.execute(
                text("ALTER TABLE study_task ADD COLUMN user_id INTEGER REFERENCES user(id)")
            )

    # Create default user 'pankaj' if no user exists so original tasks are preserved
    if User.query.count() == 0:
        default_admin = User(
            username="pankaj",
            fullname="Pankaj Kharwar",
            password_hash=generate_password_hash("pankaj123"),
            is_admin=True
        )
        db.session.add(default_admin)
        db.session.commit()

        # Link any existing unlinked tasks to Pankaj
        StudyTask.query.filter(StudyTask.user_id.is_(None)).update({"user_id": default_admin.id})
        db.session.commit()


if __name__ == "__main__":
    app.run(debug=True)
