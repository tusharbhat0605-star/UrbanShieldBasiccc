from flask import Flask, render_template, request, redirect, url_for, Response, session
import os
import time
import threading
from functools import wraps

from detector import process_video
from detector_rtsp import generate_rtsp_frames

from db import (
    init_db,
    save_detection,
    get_all_detections,
    get_detection_by_id,
    get_dashboard_stats,
    get_top_alert_runs
)

app = Flask(__name__)
app.secret_key = "urban_shield_secret_key"

# ----------------------------
# ADMIN LOGIN CONFIG
# ----------------------------
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "1234"

# ----------------------------
# FOLDERS
# ----------------------------
UPLOAD_FOLDER = "static/uploads"
OUTPUT_FOLDER = "static/output"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Initialize database
init_db()

# In-memory jobs
JOBS = {}

# ----------------------------
# LOGIN REQUIRED DECORATOR
# ----------------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# ----------------------------
# LOGIN ROUTES
# ----------------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid credentials"

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))


# ----------------------------
# HOME (UPLOAD PAGE)
# ----------------------------
@app.route("/")
@login_required
def home():
    total_runs, total_alerts, latest = get_dashboard_stats()
    return render_template("index.html", total_alerts=total_alerts)


# ----------------------------
# VIDEO PROCESSING THREAD
# ----------------------------
def run_detection_job(job_id, input_path, input_filename, output_basename, settings):
    alerts, mp4_filename = process_video(
        input_path, OUTPUT_FOLDER, output_basename, settings
    )

    output_video = f"output/{mp4_filename}"
    alert_count = len(alerts)
    created_at = time.strftime("%Y-%m-%d %H:%M:%S")

    JOBS[job_id]["status"] = "done"
    JOBS[job_id]["input_filename"] = input_filename
    JOBS[job_id]["output_video"] = output_video
    JOBS[job_id]["alerts"] = alerts
    JOBS[job_id]["alert_count"] = alert_count
    JOBS[job_id]["settings"] = settings

    save_detection(created_at, input_filename, output_video, alert_count, alerts)


# ----------------------------
# UPLOAD ROUTE
# ----------------------------
@app.route("/upload", methods=["POST"])
@login_required
def upload():
    if "video" not in request.files:
        return "No file uploaded!"

    file = request.files["video"]
    if file.filename == "":
        return "No file selected!"

    settings = {
        "stop_time": int(request.form.get("stop_time", 2)),
        "sudden_stop_speed": int(request.form.get("sudden_stop_speed", 15)),
        "stop_speed": int(request.form.get("stop_speed", 3)),
    }

    input_filename = file.filename
    input_path = os.path.join(UPLOAD_FOLDER, input_filename)
    file.save(input_path)

    timestamp = int(time.time())
    job_id = str(timestamp)
    output_basename = f"output_{timestamp}"

    JOBS[job_id] = {
        "status": "processing",
        "input_filename": input_filename,
        "output_video": None,
        "alerts": [],
        "alert_count": 0,
        "settings": settings,
    }

    t = threading.Thread(
        target=run_detection_job,
        args=(job_id, input_path, input_filename, output_basename, settings),
        daemon=True,
    )
    t.start()

    return redirect(url_for("processing", job_id=job_id))


# ----------------------------
# PROCESSING PAGE
# ----------------------------
@app.route("/processing/<job_id>")
@login_required
def processing(job_id):
    if job_id not in JOBS:
        return "Invalid job ID!"

    job = JOBS[job_id]

    if job["status"] == "done":
        return redirect(url_for("result", job_id=job_id))

    return render_template("processing.html", job_id=job_id)


# ----------------------------
# RESULT PAGE
# ----------------------------
@app.route("/result/<job_id>")
@login_required
def result(job_id):
    if job_id not in JOBS:
        return "Invalid job ID!"

    job = JOBS[job_id]

    if job["status"] != "done":
        return redirect(url_for("processing", job_id=job_id))

    return render_template(
        "result.html",
        input_filename=job["input_filename"],
        output_video=job["output_video"],
        alerts=job["alerts"],
        alert_count=job["alert_count"],
    )


# ----------------------------
# DASHBOARD
# ----------------------------
@app.route("/dashboard")
@login_required
def dashboard():
    total_runs, total_alerts, latest = get_dashboard_stats()
    top_runs = get_top_alert_runs(5)

    return render_template(
        "dashboard.html",
        total_runs=total_runs,
        total_alerts=total_alerts,
        latest=latest,
        top_runs=top_runs,
    )


# ----------------------------
# HISTORY
# ----------------------------
@app.route("/history")
@login_required
def history():
    detections = get_all_detections()
    return render_template("history.html", detections=detections)


@app.route("/history/<int:detection_id>")
@login_required
def history_detail(detection_id):
    row = get_detection_by_id(detection_id)
    if not row:
        return "Not found!"

    det_id, created_at, input_filename, output_video, alert_count, alerts_text = row
    alerts = alerts_text.split("\n") if alerts_text else []

    return render_template(
        "history_detail.html",
        created_at=created_at,
        input_filename=input_filename,
        output_video=output_video,
        alert_count=alert_count,
        alerts=alerts,
    )


# ----------------------------
# RTSP MODE
# ----------------------------
@app.route("/rtsp", methods=["GET", "POST"])
@login_required
def rtsp():
    if request.method == "POST":
        rtsp_url = request.form.get("rtsp_url")
        return render_template("rtsp.html", rtsp_url=rtsp_url)

    return render_template("rtsp.html", rtsp_url=None)


@app.route("/rtsp_feed")
@login_required
def rtsp_feed():
    rtsp_url = request.args.get("url")

    return Response(
        generate_rtsp_frames(rtsp_url),
        mimetype="multipart/x-mixed-replace; boundary=frame",
    )


# ----------------------------
# RUN APP
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True)