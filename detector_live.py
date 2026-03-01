import cv2
import math
from ultralytics import YOLO

model = YOLO("yolov8n.pt")
VEHICLE_CLASSES = ["car", "motorcycle", "bus", "truck"]


def generate_live_frames(settings=None):
    """
    Generator for MJPEG streaming in Flask.
    Reads webcam frames and yields JPEG bytes.

    settings example:
    {
        "stop_time": 2,
        "sudden_stop_speed": 15,
        "stop_speed": 3
    }
    """

    if settings is None:
        settings = {}

    STOP_TIME_SECONDS = int(settings.get("stop_time", 2))
    SUDDEN_STOP_PREV_SPEED = int(settings.get("sudden_stop_speed", 15))
    STOP_SPEED_THRESHOLD = int(settings.get("stop_speed", 3))

    cap = cv2.VideoCapture(0)  # 0 = laptop camera

    if not cap.isOpened():
        raise RuntimeError("Could not open webcam.")

    prev_centers = {}
    prev_speeds = {}
    stopped_frames = {}

    fps = 25  # webcam fps estimate

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

            if label in VEHICLE_CLASSES:
                object_id = i

                speed = 0
                if object_id in prev_centers:
                    px, py = prev_centers[object_id]
                    speed = math.sqrt((cx - px) ** 2 + (cy - py) ** 2)

                prev_centers[object_id] = (cx, cy)

                prev_speed = prev_speeds.get(object_id, 0)
                prev_speeds[object_id] = speed

                sudden_stop = (prev_speed > SUDDEN_STOP_PREV_SPEED and speed < STOP_SPEED_THRESHOLD)

                if sudden_stop:
                    stopped_frames[object_id] = 1
                elif speed < STOP_SPEED_THRESHOLD and object_id in stopped_frames:
                    stopped_frames[object_id] += 1
                elif speed >= STOP_SPEED_THRESHOLD and object_id in stopped_frames:
                    stopped_frames.pop(object_id)

                if object_id in stopped_frames:
                    if stopped_frames[object_id] >= int(fps * STOP_TIME_SECONDS):
                        accident_detected = True

                # Draw box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    frame,
                    f"{label} speed:{int(speed)}",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2
                )

        if accident_detected:
            cv2.putText(
                frame,
                "LIVE ALERT: POSSIBLE ACCIDENT",
                (30, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.1,
                (0, 0, 255),
                3
            )

        # Convert frame to JPEG
        _, buffer = cv2.imencode(".jpg", frame)
        frame_bytes = buffer.tobytes()

        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

    cap.release()
