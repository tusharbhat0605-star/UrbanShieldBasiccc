import cv2
import math
import os
import time
from ultralytics import YOLO
from notifier import send_alert_email
from db import save_detection

model = YOLO("yolov8n.pt")
VEHICLE_CLASSES = ["car", "motorcycle", "bus", "truck"]


def generate_rtsp_frames(rtsp_url, settings=None):

    if settings is None:
        settings = {}

    STOP_TIME_SECONDS = int(settings.get("stop_time", 2))
    SUDDEN_STOP_PREV_SPEED = int(settings.get("sudden_stop_speed", 15))
    STOP_SPEED_THRESHOLD = int(settings.get("stop_speed", 3))

    # Demo mode
    if rtsp_url == "demo":
        cap = cv2.VideoCapture("static/uploads/demo.mp4")
    else:
        cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        print("RTSP connection failed.")
        return

    prev_centers = {}
    prev_speeds = {}
    stopped_frames = {}

    fps = 25
    frame_count = 0
    last_alert_time = 0  # time-based instead of frame-based

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        results = model(frame, verbose=False)[0]
        accident_detected = False

        for i, box in enumerate(results.boxes):

            cls_id = int(box.cls[0])
            label = model.names[cls_id]

            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            if label in VEHICLE_CLASSES:

                object_id = i
                speed = 0

                if object_id in prev_centers:
                    px, py = prev_centers[object_id]
                    speed = math.sqrt((cx - px) ** 2 + (cy - py) ** 2)

                prev_centers[object_id] = (cx, cy)

                prev_speed = prev_speeds.get(object_id, 0)
                prev_speeds[object_id] = speed

                sudden_stop = (
                    prev_speed > SUDDEN_STOP_PREV_SPEED
                    and speed < STOP_SPEED_THRESHOLD
                )

                if sudden_stop:
                    stopped_frames[object_id] = 1
                elif speed < STOP_SPEED_THRESHOLD and object_id in stopped_frames:
                    stopped_frames[object_id] += 1
                elif speed >= STOP_SPEED_THRESHOLD and object_id in stopped_frames:
                    stopped_frames.pop(object_id)

                if object_id in stopped_frames:
                    if stopped_frames[object_id] >= int(fps * STOP_TIME_SECONDS):
                        accident_detected = True

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # -------------------------
        # 🚨 ALERT HANDLING
        # -------------------------
        if accident_detected:

            current_time = time.time()

            # Only trigger once every 10 seconds
            if current_time - last_alert_time > 10:

                print("ACCIDENT CONFIRMED - Triggering alert")

                timestamp = time.strftime("%Y%m%d_%H%M%S")
                evidence_folder = "static/evidence"
                os.makedirs(evidence_folder, exist_ok=True)

                snapshot_path = os.path.join(
                    evidence_folder,
                    f"rtsp_alert_{timestamp}.jpg"
                )

                cv2.imwrite(snapshot_path, frame)

                # Safe email sending
                try:
                    send_alert_email(
                        snapshot_path,
                        time.strftime("%Y-%m-%d %H:%M:%S"),
                        source="RTSP Mode"
                    )
                    print("EMAIL SENT SUCCESSFULLY")
                except Exception as e:
                    print("EMAIL ERROR:", e)

                # Safe DB save
                try:
                    save_detection(
                        time.strftime("%Y-%m-%d %H:%M:%S"),
                        "RTSP Stream",
                        snapshot_path,
                        1,
                        ["RTSP Accident Detected"]
                    )
                    print("DATABASE UPDATED")
                except Exception as e:
                    print("DB ERROR:", e)

                last_alert_time = current_time

            cv2.putText(
                frame,
                "RTSP ALERT: POSSIBLE ACCIDENT",
                (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.1,
                (0, 0, 255),
                3
            )

        _, buffer = cv2.imencode(".jpg", frame)
        frame_bytes = buffer.tobytes()

        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n"
            + frame_bytes +
            b"\r\n"
        )

    cap.release()