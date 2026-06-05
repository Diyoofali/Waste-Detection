from flask import Flask, render_template, request, send_file
from ultralytics import YOLO
import os
import shutil

app = Flask(__name__)

# Load model
model = YOLO("best.pt")

UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "results"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():

    # Save captured image
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

    # YOLO output folder
    predict_folder = str(results[0].save_dir)

    print("YOLO SAVE DIR:", predict_folder)

    # Find image file created by YOLO
    detected_image = None

    for file in os.listdir(predict_folder):
        if file.lower().endswith((".jpg", ".jpeg", ".png")):
            detected_image = os.path.join(
                predict_folder,
                file
            )
            break

    if detected_image is None:
        return "No detection image found!", 500

    # Copy to fixed location
    final_output = os.path.join(
        RESULT_FOLDER,
        "detected.jpg"
    )

    shutil.copy(
        detected_image,
        final_output
    )

    return "Detection Complete"


@app.route("/result")
def result():

    result_path = os.path.join(
        RESULT_FOLDER,
        "detected.jpg"
    )

    if os.path.exists(result_path):
        return send_file(
            result_path,
            mimetype="image/jpeg"
        )

    return "No result available yet."


if __name__ == "__main__":
    app.run(debug=True)
