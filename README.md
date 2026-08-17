# UrbanShield – AI-Based CCTV Monitoring & Incident Detection

> 🚧 **Work in Progress**

UrbanShield is an AI-based CCTV monitoring and incident detection system designed to analyze video streams and identify potentially dangerous incidents such as vehicle-related accidents.

The project combines **Python, Flask, OpenCV, YOLO, FFmpeg, and SQLite** to process video, perform object detection, store detection information, and provide alerts through a web-based interface.

---

## 📌 About the Project

Traditional CCTV systems require continuous human monitoring, which can make it difficult to identify incidents quickly.

UrbanShield aims to assist with this process by automatically analyzing video input and detecting potential incidents using computer vision.

The system can work with:

* Uploaded video files
* Live video processing
* RTSP camera streams

When a potential incident is detected, the system can generate evidence and trigger an alert.

---

## ✨ Features

### 🎥 Video & Camera Processing

* Uploaded video processing
* Live video processing
* RTSP stream processing
* OpenCV-based frame processing
* FFmpeg-based video conversion

### 🤖 AI & Computer Vision

* YOLO-based object detection
* Vehicle detection
* Detection of potential accident situations
* Real-time video analysis
* Evidence snapshot generation

### 🚨 Alert System

* Automatic incident alerts
* Email notifications
* Detection timestamp information
* Evidence image attached to alerts

### 📊 Dashboard & History

* Flask-based web dashboard
* Detection history
* Detection details
* Incident statistics
* SQLite database integration

### 🔐 Administration

* Admin login
* Protected dashboard access

---

## 🛠️ Tech Stack

### Backend

* Python
* Flask

### Computer Vision & AI

* YOLO
* Ultralytics
* OpenCV

### Video Processing

* FFmpeg

### Database

* SQLite

### Notifications

* SMTP
* Python `smtplib`

### Frontend

* HTML
* CSS
* JavaScript
* Flask Templates

---

## 🏗️ System Architecture

```text
              CCTV / Video Input
                       │
          ┌────────────┴────────────┐
          │                         │
     Video File                 RTSP Stream
          │                         │
          └────────────┬────────────┘
                       │
                       ▼
                OpenCV Processing
                       │
                       ▼
                YOLO Detection
                       │
                       ▼
              Incident Detection
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
       Evidence Image       Alert System
             │                   │
             │                   ▼
             │             Email Notification
             │
             ▼
        SQLite Database
             │
             ▼
       Flask Web Dashboard
```

---

## 📂 Project Structure

```text
UrbanShieldBasiccc/
│
├── app.py
├── db.py
├── detector.py
├── detector_live.py
├── detector_rtsp.py
├── notifier.py
├── requirements.txt
│
├── templates/
│
├── .gitignore
├── README.md
└── ...
```

### Main Files

| File               | Purpose                             |
| ------------------ | ----------------------------------- |
| `app.py`           | Flask web application and dashboard |
| `detector.py`      | Main video detection logic          |
| `detector_live.py` | Live video detection                |
| `detector_rtsp.py` | RTSP stream processing              |
| `notifier.py`      | Email alert functionality           |
| `db.py`            | SQLite database operations          |
| `templates/`       | Web application templates           |
| `requirements.txt` | Python dependencies                 |

---

## 🚀 Getting Started

### Prerequisites

Make sure you have:

* Python 3.x
* pip
* FFmpeg
* A compatible YOLO model
* Webcam/video file or RTSP stream for testing

### 1. Clone the Repository

```bash
git clone https://github.com/tusharbhat0605/UrbanShieldBasiccc.git
```

### 2. Navigate to the Project

```bash
cd UrbanShieldBasiccc
```

### 3. Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a local `.env` file:

```env
SENDER_EMAIL=your_email
APP_PASSWORD=your_app_password
RECEIVER_EMAIL=receiver_email
```

> Never commit the `.env` file or private credentials to GitHub.

### 5. Run the Application

```bash
python app.py
```

Open the Flask application in your browser using the address shown in the terminal.

---

## 🔐 Security

UrbanShield uses environment variables for sensitive email configuration.

The following values are loaded from `.env`:

```text
SENDER_EMAIL
APP_PASSWORD
RECEIVER_EMAIL
```

The `.env` file is excluded from version control using `.gitignore`.

---

## 🧠 Key Development Areas

This project provided hands-on experience with:

* Python backend development
* Flask web applications
* Computer vision
* YOLO object detection
* OpenCV video processing
* RTSP stream processing
* Real-time video analysis
* SQLite database operations
* Email notification systems
* Video processing with FFmpeg
* Integrating AI models into web applications

---

## 🚧 Current Development Status

UrbanShield is currently **under active development**.

### Current Implementation

* Flask web application
* YOLO-based object detection
* Vehicle detection
* Video processing
* RTSP stream processing
* Detection history
* SQLite database
* Email alert system
* Admin dashboard

### Areas Being Improved

* Detection accuracy
* False-positive reduction
* Real-time processing performance
* Incident detection reliability
* Dashboard improvements
* Overall system optimization

---

## 🎯 Project Goal

The long-term goal of UrbanShield is to develop an intelligent CCTV monitoring system that can assist in identifying potentially dangerous incidents automatically and provide timely alerts to relevant users.

---

## 🔮 Future Improvements

Potential future improvements include:

* Improved accident detection accuracy
* Additional incident types such as fire detection
* More advanced real-time analytics
* Improved RTSP stream handling
* Advanced dashboard analytics
* Multiple camera support
* Improved notification mechanisms
* Performance optimization

---

## 👨‍💻 Developer

**Tushar Bhat**

Information Science Engineering Student

### Areas of Interest

* Python Development
* Backend Development
* Artificial Intelligence
* Machine Learning
* Computer Vision
* Mobile Application Development

---

## 📄 License

This project is currently being developed as a personal/academic project for learning and demonstration purposes.
