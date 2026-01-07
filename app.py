from flask import Flask, render_template, request, send_file
import os
from attendance_logic import process_attendance

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        z_file = request.files.get("zfile")
        r_file = request.files.get("rfile")

        if not z_file or not r_file:
            return "Please upload both files"

        z_path = os.path.join(UPLOAD_FOLDER, z_file.filename)
        r_path = os.path.join(UPLOAD_FOLDER, r_file.filename)

        z_file.save(z_path)
        r_file.save(r_path)

        clean_file, attendance_file, summary = process_attendance(
            z_path, r_path, OUTPUT_FOLDER
        )

        return render_template(
            "result.html",
            clean_file=clean_file,
            attendance_file=attendance_file,
            summary=summary
        )

    return render_template("index.html")


@app.route("/download")
def download():
    file_path = request.args.get("file")
    return send_file(file_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
