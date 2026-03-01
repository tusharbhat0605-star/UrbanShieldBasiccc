import cv2
import math
import os
import subprocess
import time
from ultralytics import YOLO
from notifier import send_alert_email

model = YOLO("yolov8n.pt")
VEHICLE_CLASSES = ["car", "motorcycle", "bus", "truck"]


def convert_avi_to_mp4(avi_path, mp4_path):
    cmd = [
        "ffmpeg",
        "-y",
        "-i", avi_path,
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        mp4_path
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def process_video(input_path, output_folder, output_basename, settings=None):

    if settings is None:
        settings = {}

    STOP_TIME_SECONDS = int(settings.get("stop_time", 2))
    SUDDEN_STOP_PREV_SPEED = int(settings.get("sudden_stop_speed", 15))
    STOP_SPEED_THRESHOLD = int(settings.get("stop_speed", 3))

    cap = cv2.VideoCapture(input_path)

    if not cap.isOpened():
        print("ERROR: Could not open input video:", input_path)
        return [], None

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    if fps == 0:
        fps = 25

    avi_filename = f"{output_basename}.avi"
    avi_path = os.path.join(output_folder, avi_filename)

    fourcc = cv2.VideoWriter_fourcc(*"MJPG")
    out = cv2.VideoWriter(avi_path, fourcc, fps, (width, height))

    if not out.isOpened():
        print("ERROR: VideoWriter could not open.")
        return [], None

    prev_centers = {}
    prev_speeds = {}
    stopped_frames = {}

    alerts = []
    last_alert_frame = -9999

    frame_count = 0

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

            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

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
                    prev_speed > SUDDEN_STOP_PREV_SPEED and
                    speed < STOP_SPEED_THRESHOLD
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

                cv2.putText(
                    frame,
                    f"{label} speed:{int(speed)}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

            else:
                cv2.putText(
                    frame,
                    label,
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

        # --------------------------
        # ALERT BLOCK (FIXED)
        # --------------------------
        if accident_detected:

            # Avoid spamming every frame
            if frame_count - last_alert_frame > int(fps * 5):

                timestamp = time.strftime("%Y%m%d_%H%M%S")
                evidence_folder = "static/evidence"
                os.makedirs(evidence_folder, exist_ok=True)

                snapshot_path = os.path.join(
                    evidence_folder,
                    f"upload_alert_{timestamp}.jpg"
                )

                cv2.imwrite(snapshot_path, frame)

                send_alert_email(
                    snapshot_path,
                    time.strftime("%Y-%m-%d %H:%M:%S"),
                    source="Upload Mode"
                )

                seconds = frame_count / fps
                mm = int(seconds // 60)
                ss = int(seconds % 60)
                alerts.append(
                    f"{mm:02d}:{ss:02d} -> POSSIBLE ACCIDENT DETECTED"
                )

                last_alert_frame = frame_count

            cv2.putText(
                frame,
                "POSSIBLE ACCIDENT DETECTED",
                (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.1,
                (0, 0, 255),
                3
            )

        out.write(frame)

    cap.release()
    out.release()

    mp4_filename = f"{output_basename}.mp4"
    mp4_path = os.path.join(output_folder, mp4_filename)

    convert_avi_to_mp4(avi_path, mp4_path)

    return alerts, mp4_filename