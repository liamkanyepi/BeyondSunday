from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime
import uuid

# Configuration
app = Flask(__name__, static_folder="static")
CORS(app)  # Enable CORS for frontend access
UPLOAD_FOLDER = "uploads"
STORY_DURATION_MS = 50000  # 5 seconds
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ---- FRONTEND ROUTES ----

@app.route('/')
def serve_login():
    """Serve the login page as the landing page"""
    return send_from_directory(app.static_folder, 'login.html')


@app.route('/upload')
def serve_upload():
    """Serve the upload page after login"""
    return send_from_directory(app.static_folder, 'upload.html')


# ---- API ROUTES ----

@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    """Handle photo upload and save to directory"""
    if 'photo' not in request.files:
        return jsonify({"error": "No photo provided"}), 400

    file = request.files['photo']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if file and allowed_file(file.filename):
        # Generate unique filename using UUID and timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        filename = f"photo_{timestamp}_{unique_id}.{file.filename.rsplit('.', 1)[1].lower()}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        try:
            file.save(file_path)
            return jsonify({
                "status": "success",
                "filename": filename,
                "story_duration_ms": STORY_DURATION_MS # ✅ CORRECTED
            }), 200
        except Exception as e:
            return jsonify({"error": f"Failed to save photo: {str(e)}"}), 500
    else:
        return jsonify({"error": "Invalid file format. Allowed formats: png, jpg, jpeg, gif"}), 400


@app.route('/uploads/<filename>')
def serve_uploaded_file(filename):
    """Serve uploaded photo files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ---- SERVER START ----

if __name__ == '__main__':
    print(f"Starting server...")
    print(f"Photos will be saved in: {UPLOAD_FOLDER}")
    print(f"Story duration is set to {STORY_DURATION_MS}ms") # ✅ CORRECTED
    print(f"Access login page at: http://localhost:5000")
    print(f"Access upload page directly at: http://localhost:5000/upload")
    app.run(host='0.0.0.0', port=5000, debug=True)