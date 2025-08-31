import os
import re
import pytesseract
from PIL import Image
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from datetime import datetime
from app.model import Prescription, User
from app import sessionLocal

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Blueprint
prescription_bp = Blueprint('prescription', __name__)
UPLOAD_FOLDER = os.path.join("app", "static", "uploads")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# --- Helpers ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def compress_image(path):
    img = Image.open(path)
    img = img.convert('L')  # Grayscale
    img.thumbnail((800, 800))
    img.save(path)

def extract_medicines(text):
    pattern = r'\b([A-Z][a-zA-Z]{2,})\b.*?(\d+mg|\d+ml|\d+g)?'
    ignore_words = {"take", "tablet", "daily", "twice", "once", "after", "before", "every", "night", "day"}

    results = []
    for name, dose in re.findall(pattern, text):
        if name.lower() not in ignore_words:
            results.append({"name": name, "dosage": dose.strip() if dose else ""})
    return results

def simple_disease_match(text):
    text = text.lower()
    if "cough" in text or "fever" in text:
        return "Flu"
    elif "sugar" in text or "glucose" in text:
        return "Diabetes"
    elif "breath" in text or "wheezing" in text:
        return "Asthma"
    elif "pressure" in text:
        return "Hypertension"
    return "Unknown"

# --- Route ---
@prescription_bp.route('/upload_prescription', methods=['GET', 'POST'])
def upload_prescription():
    if 'user' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('register.login'))

    db = sessionLocal()
    user = db.query(User).filter_by(username=session['user']).first()
    if not user:
        flash("User not found!", "danger")
        return redirect(url_for('register.login'))

    analysis_result = None

    if request.method == 'POST':
        prescription_name = request.form['prescription_name']
        file = request.files['image']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            relative_path = os.path.join("uploads", filename)
            file.save(file_path)

            try:
                compress_image(file_path)

                img = Image.open(file_path).convert("L")
                ocr_text = pytesseract.image_to_string(img, lang='eng', config='--psm 6')

                medicines = extract_medicines(ocr_text)
                predicted_disease = simple_disease_match(ocr_text)

                # Save to DB
                new_prescription = Prescription(
                    user_id=user.id,
                    prescription_name=prescription_name,
                    image_url=relative_path,  # ✅ Store relative path only
                    ocr_text=ocr_text,
                    predicted_disease=predicted_disease,
                    medicines_json=medicines,
                    uploaded_at=datetime.utcnow()
                )
                db.add(new_prescription)
                db.commit()

                analysis_result = {
                    "text": ocr_text,
                    "predicted_disease": predicted_disease,
                    "medicines": medicines
                }

                flash("Prescription uploaded & analyzed!", "success")

            except Exception as e:
                print("Error during processing:", e)  # ✅ For debug
                flash(f"Error: {str(e)}", "danger")
        else:
            flash("Invalid file type.", "danger")

    prescriptions = db.query(Prescription).filter_by(user_id=user.id).all()
    return render_template("upload_prescription.html", prescriptions=prescriptions, user=user, analysis=analysis_result)
