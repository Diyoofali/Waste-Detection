from flask import Flask, render_template, request, send_file
from ultralytics import YOLO
from datetime import datetime
import sqlite3
import os
import shutil
import uuid

app = Flask(__name__)

# Load YOLO model
model = YOLO("best.pt")

UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "results"
STATIC_DETECTION_FOLDER = os.path.join(
    "static",
    "detections"
)

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)
os.makedirs(STATIC_DETECTION_FOLDER, exist_ok=True)


def save_detection(
    image_name,
    category,
    confidence
):

    conn = sqlite3.connect("waste.db")

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO detections
        (
            image_name,
            category,
            confidence,
            timestamp
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            image_name,
            category,
            confidence,
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )
    )

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():

    image_path = os.path.join(
        UPLOAD_FOLDER,
        "captured.jpg"
    )

    with open(image_path, "wb") as f:
        f.write(request.data)

    # Run YOLO
    results = model.predict(
        source=image_path,
        save=True
    )

    predict_folder = str(
        results[0].save_dir
    )

    detected_image = None

    for file in os.listdir(
        predict_folder
    ):

        if file.lower().endswith(
            (
                ".jpg",
                ".jpeg",
                ".png"
            )
        ):
            detected_image = os.path.join(
                predict_folder,
                file
            )
            break

    if detected_image is None:
        return (
            "No detection image found",
            500
        )

    # Unique image name
    image_name = (
        str(uuid.uuid4()) + ".jpg"
    )

    dashboard_image = os.path.join(
        STATIC_DETECTION_FOLDER,
        image_name
    )

    shutil.copy(
        detected_image,
        dashboard_image
    )

    # Latest result image
    final_output = os.path.join(
        RESULT_FOLDER,
        "detected.jpg"
    )

    shutil.copy(
        detected_image,
        final_output
    )

    # Save detections to DB
    for box in results[0].boxes:

        class_id = int(
            box.cls[0]
        )

        category = model.names[
            class_id
        ]

        confidence = float(
            box.conf[0]
        )

        save_detection(
            image_name,
            category,
            confidence
        )

    return "Detection Complete"


@app.route("/result")
def result():

    result_path = os.path.join(
        RESULT_FOLDER,
        "detected.jpg"
    )

    if os.path.exists(
        result_path
    ):
        return send_file(
            result_path,
            mimetype="image/jpeg"
        )

    return "No result available"


@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect(
        "waste.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM detections
        ORDER BY id DESC
        """
    )

    detections = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        detections=detections
    )


if __name__ == "__main__":
    app.run(debug=True)