from flask import Flask, render_template, request, jsonify
import json
import os
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import base64
import logging

app = Flask(__name__, static_folder="static", template_folder="templates")

def check_url_safety(url):
    """Custom rule-based URL safety check"""

    
    restricted_urls = [  "https://192.168.212.202:8443/"
    
    ]

    if url in restricted_urls:
        return False, {"info": "This link is flagged as unsafe"}

    
    return True, {"info": "This URL is safe and secured"}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/check_url', methods=['POST'])
def check_url():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    safe, details = check_url_safety(url)
    result = {
        "qr_data": url,
        "safe": safe,
        "details": details if not safe else "Safe and secured"
    }

    if not safe:
        result["message"] = "Defective or unsafe link"

    return jsonify(result)


@app.route('/scan_qr', methods=['POST'])
def scan_qr():
    try:
        data = request.get_json()
        img_data = data.get('image')
        if not img_data:
            return jsonify({'error': 'No image data provided'}), 400

        header, encoded = img_data.split(',', 1)
        img_bytes = base64.b64decode(encoded)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

       
        decoded_objects = decode(img)
        if not decoded_objects:
            return jsonify({
                'qr_data': None,
                'safe': False,
                'no_qr': True,
                'message': 'No QR code detected',
                'details': 'No QR code detected in the image'
            }), 200

        qr_data = decoded_objects[0].data.decode('utf-8')

        
        analysis = {
            "length": len(qr_data),
            "type": "URL" if qr_data.startswith("http") else "Text",
            "content_preview": qr_data[:50] + ("..." if len(qr_data) > 50 else "")
        }

        
        safe, details = check_url_safety(qr_data)
        result = {
            "qr_data": qr_data,
            "safe": safe,
            "details": details if not safe else "Safe and secured",
            "analysis": analysis
        }

        if not safe:
            result["message"] = "Defective or unsafe link"

        return jsonify(result)
    except Exception as e:
        logging.exception("Error in scan_qr endpoint")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500


@app.route('/scan_qr_realtime', methods=['POST'])
def scan_qr_realtime():
    try:
        data = request.get_json()
        img_data = data.get('image')
        if not img_data:
            return jsonify({'qr_data': None, 'safe': False, 'details': 'No image data provided'})

        
        header, encoded = img_data.split(',', 1)
        img_bytes = base64.b64decode(encoded)
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        
        decoded_objects = decode(img)
        if not decoded_objects:
            return jsonify({
                'qr_data': None,
                'safe': False,
                'no_qr': True,
                'message': 'No QR code detected',
                'details': 'No QR code detected in the image'
            })

        qr_data = decoded_objects[0].data.decode('utf-8')

        
        analysis = {
            "length": len(qr_data),
            "type": "URL" if qr_data.startswith("http") else "Text",
            "content_preview": qr_data[:50] + ("..." if len(qr_data) > 50 else "")
        }

        
        safe, details = check_url_safety(qr_data)
        result = {
            "qr_data": qr_data,
            "safe": safe,
            "details": details if not safe else "Safe and secured",
            "analysis": analysis
        }

        if not safe:
            result["message"] = "Defective or unsafe link"

        return jsonify(result)
    except Exception as e:
        logging.exception("Error in scan_qr_realtime endpoint")
        return jsonify({'qr_data': None, 'safe': False, 'details': 'Error processing image'})


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True)
