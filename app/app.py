from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime
import uuid

# Import AI Classes
# NOTE: Make sure the VLM_devotional file is the updated version from the previous step
from scripture_suggestion.VLM_scripture import Scripture_VLM
from scripture_suggestion.VLM_devotional import Devotional_VLM

# Configuration
app = Flask(__name__, static_folder="static")
CORS(app)  # Enable CORS for frontend access
UPLOAD_FOLDER = "uploads"
STORY_DURATION_MS = 50000  # 50 seconds
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize AI models once
vlm = Scripture_VLM()
devotional_vlm = Devotional_VLM()


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


@app.route('/devotional')
def serve_devotional():
    """Serve the devotional page"""
    return send_from_directory(app.static_folder, 'devotional.html')


# ---- API ROUTES ----

@app.route('/upload_photo', methods=['POST'])
def upload_photo():
    """Handle photo upload, save to directory, and return multiple scriptures"""
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
            # Save the photo locally
            file.save(file_path)

            # Call Scripture AI model (returns list of verses or rejection message)
            scriptures = vlm.generate_scripture(file_path, num_verses=3)

            return jsonify({
                "status": "success",
                "filename": filename,
                "story_duration_ms": STORY_DURATION_MS,
                "scriptures": scriptures  # <-- return list for dropdown
            }), 200

        except Exception as e:
            return jsonify({"error": f"Failed to save photo or generate scriptures: {str(e)}"}), 500

    else:
        return jsonify({"error": "Invalid file format. Allowed formats: png, jpg, jpeg, gif"}), 400


# --- THIS IS THE MODIFIED SECTION ---
@app.route('/generate_devotional', methods=['POST'])
def generate_devotional():
    """Generate a devotional based on topic, feeling, and optional image"""
    try:
        topic = request.form.get("topic")
        feeling = request.form.get("feeling")
        # 1. Get the 'force_generation' flag from the form data.
        # It defaults to False if not present (for the first request).
        force_generation = request.form.get('force_generation') == 'true'

        if not topic or not feeling:
            return jsonify({"status": "error", "content": "Topic and feeling are required"}), 400

        image_path = None
        if "photo" in request.files and request.files["photo"].filename != "":
            file = request.files["photo"]
            if file and allowed_file(file.filename):
                # Save optional photo
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                unique_id = str(uuid.uuid4())[:8]
                filename = f"devotional_{timestamp}_{unique_id}.{file.filename.rsplit('.', 1)[1].lower()}"
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(image_path)
            else:
                return jsonify({"status": "error", "content": "Invalid file format for devotional image."}), 400

        # 2. Call the devotional VLM, passing the force_generation flag.
        response_data = devotional_vlm.generate_devotional(
            topic=topic,
            feeling=feeling,
            image_path=image_path,
            force_generation=force_generation
        )

        # 3. Return the dictionary from the VLM class directly.
        # The front-end is already set up to handle this structure.
        return jsonify(response_data), 200

    except Exception as e:
        # Return errors in the same status/content format for consistency.
        return jsonify({"status": "error", "content": f"An unexpected server error occurred: {str(e)}"}), 500


@app.route('/uploads/<filename>')
def serve_uploaded_file(filename):
    """Serve uploaded photo files"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ---- SERVER START ----

if __name__ == '__main__':
    print(f"Starting server...")
    print(f"Photos will be saved in: {UPLOAD_FOLDER}")
    print(f"Story duration is set to {STORY_DURATION_MS}ms")
    print(f"Access login page at: http://localhost:8000")
    print(f"Access upload page directly at: http://localhost:8000/upload")
    print(f"Access devotional page at: http://localhost:8000/devotional")
    #app.run(host='0.0.0.0', port=8000, debug=True)
    #app.run(host='0.0.0.0', port=8000)