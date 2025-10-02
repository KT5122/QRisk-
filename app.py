from flask import Flask, render_template, request, jsonify
import re
import os
import cv2
import numpy as np
from pyzbar.pyzbar import decode

app = Flask(__name__, static_folder="static", template_folder="templates")

# -------------------------------
# Helper Functions
# -------------------------------

def is_malicious_url(url: str) -> bool:
    """
    Dummy malicious URL detector.
    You can replace this with Google Safe Browsing API, VirusTotal, etc.
    """
    suspicious_patterns = ["malware", "phish", "hack", "suspicious", "fake", "danger"]
    return any(p in url.lower() for p in suspicious_patterns)

def decode_qr_from_image(file_path: str):
    """Decode QR code data from an image file."""
    try:
        img = cv2.imread(file_path)
        if img is None:
            return None
        qr_codes = decode(img)
        if qr_codes:
            return qr_codes[0].data.decode("utf-8")  # Return first QR result
        return None
    except Exception as e:
        print(f"Error decoding QR code: {e}")
        return None

# -------------------------------
# Routes
# -------------------------------

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/scan_url", methods=["POST"])
def scan_url():
    try:
        data = request.json
        url = data.get("url")

        if not url:
            return jsonify({"status": "unsafe", "message": "No URL provided."}), 400

        if is_malicious_url(url):
            return jsonify({"status": "unsafe", "message": f"⚠️ The URL '{url}' is flagged as malicious!"})
        else:
            return jsonify({"status": "safe", "message": f"✅ The URL '{url}' looks safe."})
    except Exception as e:
        return jsonify({"status": "error", "message": f"An error occurred: {str(e)}"}), 500

@app.route("/scan_qr", methods=["POST"])
def scan_qr():
    try:
        if "file" not in request.files:
            return jsonify({"status": "unsafe", "message": "No file uploaded."}), 400

        file = request.files["file"]
        if not file.filename:
            return jsonify({"status": "unsafe", "message": "No file selected."}), 400

        # Save file temporarily
        upload_dir = os.path.join(app.static_folder, "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, file.filename)
        file.save(file_path)

        # Decode QR
        qr_data = decode_qr_from_image(file_path)

        # Delete after processing
        os.remove(file_path)

        if not qr_data:
            return jsonify({"status": "unsafe", "message": "❌ Could not read any QR code from the image."})

        # Check if decoded QR data is suspicious
        if is_malicious_url(qr_data):
            return jsonify({"status": "unsafe", "message": f"⚠️ The QR code contains a malicious link: {qr_data}"})
        else:
            return jsonify({"status": "safe", "message": f"✅ The QR code contains a safe link: {qr_data}"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"An error occurred: {str(e)}"}), 500


# -------------------------------
# Run App
# -------------------------------
if __name__ == "__main__":
    app.run(debug=True)