# 📸 Beyond Sunday App

This is **Flask-based web application**  allowing users to **upload or take a photo** and select an emotion from a dropdown list. The app is mobile-friendly and can be accessed from your phone or other devices on the same network.

---

## 🚀 Features
- Upload or take a photo directly from your device.
- Select an **emotion** from a dropdown list.
- Images are saved server-side.
---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository
```bash
# Clone the repository
git clone https://github.com/yourusername/beyond-sunday.git

# Navigate to project directory
cd beyond-sunday
```

### 2️⃣ Set up Python Environment
```bash
# Create a virtual environment
python3 -m venv app_venv

# Activate the virtual environment
# On Linux/Mac:
source app_venv/bin/activate
# On Windows:
# app_venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3️⃣ Running the Application
```bash
# Navigate to the app directory
cd app

# Start the Flask server
python app.py
```

The application will be available at:
- Login page: `http://localhost:5000`
- Upload page: `http://localhost:5000/upload`

### 📝 Important Notes
- Make sure you have Python 3.7+ installed
- The server runs in debug mode by default
- Photos are stored in the `app/uploads` directory
- Images will disappear after 30 seconds (configurable in app.py)
- Supported image formats: PNG, JPG, JPEG, GIF