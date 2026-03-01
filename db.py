import sqlite3
import os

DB_NAME = "urbanshield.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS detections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        created_at TEXT,
        input_filename TEXT,
        output_video TEXT,
        alert_count INTEGER,
        alerts_text TEXT
    )
    """)

    conn.commit()
    conn.close()


def save_detection(created_at, input_filename, output_video, alert_count, alerts):
    conn = get_connection()
    cur = conn.cursor()

    alerts_text = "\n".join(alerts)

    cur.execute("""
    INSERT INTO detections (created_at, input_filename, output_video, alert_count, alerts_text)
    VALUES (?, ?, ?, ?, ?)
    """, (created_at, input_filename, output_video, alert_count, alerts_text))

    conn.commit()
    conn.close()


def get_all_detections():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT id, created_at, input_filename, output_video, alert_count
    FROM detections
    ORDER BY id DESC
    """)

    rows = cur.fetchall()
    conn.close()
    return rows


def get_detection_by_id(detection_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    SELECT id, created_at, input_filename, output_video, alert_count, alerts_text
    FROM detections
    WHERE id = ?
    """, (detection_id,))

    row = cur.fetchone()
    conn.close()
    return row

def get_dashboard_stats():
    conn = get_connection()
    cur = conn.cursor()

    # Total videos processed
    cur.execute("SELECT COUNT(*) FROM detections")
    total_runs = cur.fetchone()[0]

    # Total alerts across all runs
    cur.execute("SELECT COALESCE(SUM(alert_count), 0) FROM detections")
    total_alerts = cur.fetchone()[0]

    # Latest detection
    cur.execute("""
        SELECT created_at, input_filename, alert_count
        FROM detections
        ORDER BY id DESC
        LIMIT 1
    """)
    latest = cur.fetchone()

    conn.close()

    return total_runs, total_alerts, latest


def get_top_alert_runs(limit=5):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, created_at, input_filename, alert_count
        FROM detections
        ORDER BY alert_count DESC, id DESC
        LIMIT ?
    """, (limit,))

    rows = cur.fetchall()
    conn.close()
    return rows
