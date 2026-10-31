"""Tests for Study Planner Auth & User Data Isolation"""
import os, sys
os.chdir(r"C:\Users\Pankaj Kharwar\OneDrive\Desktop\Desktop\eSupport\Documents\smart-study-planner")
sys.path.insert(0, r"C:\Users\Pankaj Kharwar\OneDrive\Desktop\Desktop\eSupport\Documents\smart-study-planner")

from app import app, db, User, StudyTask

with app.test_client() as c:
    # 1. Accessing / without login should redirect to /login
    r = c.get("/", follow_redirects=False)
    assert r.status_code in (301, 302), f"Expected redirect, got {r.status_code}"
    print("[PASS] Unauthenticated access redirects to /login")

    # 2. Login with Pankaj's default credentials
    r = c.post("/login", data={"username": "pankaj", "password": "wrongpassword"}, follow_redirects=True)
    assert b"Invalid username" in r.data
    print("[PASS] Wrong password rejected")

    r = c.post("/login", data={"username": "pankaj", "password": "pankaj123"}, follow_redirects=True)
    assert r.status_code == 200
    assert b"Pankaj Kharwar" in r.data
    print("[PASS] Login with default user (pankaj) works")

    # 3. Create a second test user
    with app.app_context():
        u2 = User.query.filter_by(username="testuser2").first()
        if u2:
            db.session.delete(u2)
            db.session.commit()

    r = c.get("/logout", follow_redirects=True)
    r = c.post("/register", data={
        "fullname": "Aman Verma",
        "username": "testuser2",
        "password": "amanpassword"
    }, follow_redirects=True)
    assert b"Account created successfully" in r.data
    print("[PASS] New user registration works")

    # 4. Login as Aman
    r = c.post("/login", data={"username": "testuser2", "password": "amanpassword"}, follow_redirects=True)
    assert b"Aman Verma" in r.data
    # Aman should see 0 tasks initially, NOT Pankaj's 9 tasks
    assert b"No tasks created yet" in r.data
    print("[PASS] Aman cannot see Pankaj's tasks (Data isolation verified)")

    # 5. Aman adds a task
    r = c.post("/tasks/add", data={
        "title": "Aman Math Task",
        "subject": "Math",
        "duration": "45",
        "time_slot": "Morning",
        "priority": "High"
    }, follow_redirects=True)
    assert b"Aman Math Task" in r.data
    print("[PASS] Aman can add his own task")

    # 6. Switch back to Pankaj, verify Pankaj sees his tasks and NOT Aman's
    c.get("/logout", follow_redirects=True)
    r = c.post("/login", data={"username": "pankaj", "password": "pankaj123"}, follow_redirects=True)
    assert b"Aman Math Task" not in r.data
    assert b"python project" in r.data
    print("[PASS] Pankaj cannot see Aman's tasks on frontend")

    # Cleanup testuser2
    with app.app_context():
        u2 = User.query.filter_by(username="testuser2").first()
        if u2:
            db.session.delete(u2)
            db.session.commit()
    print("[PASS] Test cleanup complete")

print("\nALL AUTH & PRIVACY TESTS PASSED!")
