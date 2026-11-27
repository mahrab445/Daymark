import os
import re
from datetime import datetime
from functools import wraps
from urllib.parse import parse_qs, urlparse
from zoneinfo import ZoneInfo

from bson.objectid import ObjectId
from flask import Flask, render_template, request, redirect, url_for, session, flash
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-this-secret-key")

mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    raise RuntimeError("MONGO_URI is missing. Add it to your .env file.")

client = MongoClient(mongo_uri)
db = client[os.getenv("DB_NAME", "daily_routine_tracker")]
users = db["users"]
tasks = db["tasks"]
DHAKA_TZ = ZoneInfo("Asia/Dhaka")


def dhaka_now():
    return datetime.now(DHAKA_TZ)


def dhaka_today():
    return dhaka_now().date()


def drive_file_id_from_link(link):
    """Accept a Google Drive share URL and return its file ID."""
    try:
        parsed = urlparse(link.strip())
    except ValueError:
        return None
    if parsed.scheme not in ("http", "https") or parsed.hostname != "drive.google.com":
        return None
    match = re.search(r"/d/([A-Za-z0-9_-]+)", parsed.path)
    if match:
        return match.group(1)
    file_id = parse_qs(parsed.query).get("id", [None])[0]
    return file_id if file_id and re.fullmatch(r"[A-Za-z0-9_-]+", file_id) else None


def drive_photo_url(user):
    file_id = user.get("photo_drive_id") if user else None
    return f"https://drive.google.com/thumbnail?id={file_id}&sz=w256" if file_id else None


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or len(password) < 6:
            flash("Please complete all fields. Password must be at least 6 characters.", "error")
            return render_template("register.html")

        if users.find_one({"email": email}):
            flash("An account with this email already exists.", "error")
            return render_template("register.html")

        result = users.insert_one({
            "username": username,
            "email": email,
            "photo_drive_id": None,
            "password": generate_password_hash(password),
            "created_at": dhaka_now()
        })
        session["user_id"] = str(result.inserted_id)
        session["username"] = username
        return redirect(url_for("dashboard"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = users.find_one({"email": email})

        if user and check_password_hash(user["password"], password):
            session["user_id"] = str(user["_id"])
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))

        flash("Incorrect email or password.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    today = dhaka_today()
    today_string = today.isoformat()
    selected_date = request.args.get("date", today_string)
    try:
        selected_day = datetime.strptime(selected_date, "%Y-%m-%d").date()
    except ValueError:
        selected_date = today_string
        selected_day = today

    user_id = ObjectId(session["user_id"])
    current_user = users.find_one({"_id": user_id})
    if not current_user:
        session.clear()
        return redirect(url_for("login"))
    day_tasks = list(tasks.find({
        "user_id": user_id,
        "task_date": selected_date
    }).sort("created_at", 1))

    total = len(day_tasks)
    completed = sum(1 for task in day_tasks if task.get("completed"))
    pending = total - completed
    percentage = round((completed / total) * 100) if total else 0

    return render_template(
        "dashboard.html",
        tasks=day_tasks,
        selected_date=selected_date,
        total=total,
        completed=completed,
        pending=pending,
        percentage=percentage,
        can_add_tasks=selected_day >= today,
        can_edit_tasks=selected_day >= today,
        can_toggle_tasks=selected_day == today,
        current_user=current_user,
        photo_url=drive_photo_url(current_user),
        today=dhaka_today().isoformat()
    )


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user_id = ObjectId(session["user_id"])
    current_user = users.find_one({"_id": user_id})
    if not current_user:
        session.clear()
        return redirect(url_for("login"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        drive_link = request.form.get("drive_photo_url", "").strip()
        photo_id = drive_file_id_from_link(drive_link) if drive_link else None

        if not username or len(username) > 40:
            flash("Please enter a name up to 40 characters long.", "error")
        elif drive_link and not photo_id:
            flash("Please paste a valid Google Drive file sharing link.", "error")
        else:
            users.update_one(
                {"_id": user_id},
                {"$set": {"username": username, "photo_drive_id": photo_id}}
            )
            session["username"] = username
            flash("Profile updated.", "success")
            return redirect(url_for("profile"))

        current_user["username"] = username or current_user["username"]
        return render_template(
            "profile.html", current_user=current_user,
            photo_url=drive_photo_url(current_user), drive_photo_url_input=drive_link
        )

    return render_template(
        "profile.html", current_user=current_user,
        photo_url=drive_photo_url(current_user),
        drive_photo_url_input=(
            f"https://drive.google.com/file/d/{current_user['photo_drive_id']}/view?usp=sharing"
            if current_user.get("photo_drive_id") else ""
        )
    )


@app.route("/tasks/add", methods=["POST"])
@login_required
def add_task():
    title = request.form.get("title", "").strip()
    task_date = request.form.get("task_date", dhaka_today().isoformat())
    description = request.form.get("description", "").strip()
    task_time = request.form.get("task_time", "").strip()

    try:
        datetime.strptime(task_date, "%Y-%m-%d")
    except ValueError:
        task_date = dhaka_today().isoformat()

    if task_date < dhaka_today().isoformat():
        flash("Past dates are view-only. You can't add a task there.", "error")
        return redirect(url_for("dashboard", date=task_date))

    try:
        if task_time:
            datetime.strptime(task_time, "%H:%M")
    except ValueError:
        task_time = ""

    if title:
        tasks.insert_one({
            "user_id": ObjectId(session["user_id"]),
            "title": title,
            "description": description,
            "task_date": task_date,
            "task_time": task_time,
            "completed": False,
            "created_at": dhaka_now()
        })
    return redirect(url_for("dashboard", date=task_date))


@app.route("/tasks/toggle/<task_id>", methods=["POST"])
@login_required
def toggle_task(task_id):
    task = tasks.find_one({"_id": ObjectId(task_id), "user_id": ObjectId(session["user_id"])})
    if task and task.get("task_date") == dhaka_today().isoformat():
        tasks.update_one({"_id": task["_id"]}, {"$set": {"completed": not task.get("completed", False)}})
    elif task:
        flash("Only today's tasks can be marked complete.", "error")
    return redirect(url_for("dashboard", date=request.form.get("task_date", dhaka_today().isoformat())))


@app.route("/tasks/delete/<task_id>", methods=["POST"])
@login_required
def delete_task(task_id):
    task = tasks.find_one({"_id": ObjectId(task_id), "user_id": ObjectId(session["user_id"])})
    if task and task.get("task_date", "") >= dhaka_today().isoformat():
        tasks.delete_one({"_id": task["_id"]})
    elif task:
        flash("Past tasks are view-only and can't be changed.", "error")
    return redirect(url_for("dashboard", date=request.form.get("task_date", dhaka_today().isoformat())))


@app.route("/tasks/edit/<task_id>", methods=["POST"])
@login_required
def edit_task(task_id):
    title = request.form.get("title", "").strip()
    task_time = request.form.get("task_time", "").strip()
    task_date = request.form.get("task_date", dhaka_today().isoformat())
    try:
        if task_time:
            datetime.strptime(task_time, "%H:%M")
    except ValueError:
        task_time = ""
    task = tasks.find_one({"_id": ObjectId(task_id), "user_id": ObjectId(session["user_id"])})
    if task and task.get("task_date", "") >= dhaka_today().isoformat() and title:
        tasks.update_one(
            {"_id": task["_id"]},
            {"$set": {"title": title, "task_time": task_time}}
        )
    elif task:
        flash("Past tasks are view-only and can't be changed.", "error")
    return redirect(url_for("dashboard", date=task_date))


if __name__ == "__main__":
    app.run(debug=True)
