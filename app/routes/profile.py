from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import os
from werkzeug.utils import secure_filename
from app import sessionLocal
from app.model import Profile, User, HealthRecord

pro = Blueprint('profile', __name__)
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@pro.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' not in session:
        return redirect(url_for('register.login'))

    db = sessionLocal()
    username = session['user']
    user = db.query(User).filter_by(username=username).first()
    profile = db.query(Profile).filter_by(user_id=user.id).first()

    if request.method == 'POST':
        form = request.form
        health = db.query(HealthRecord).filter_by(user_id=user.id).order_by(HealthRecord.created_at.desc()).first()

        file = request.files.get("photo")
        photo_filename = profile.photo if profile and profile.photo else None
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            photo_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(photo_path)
            photo_filename = photo_path

        if not profile:
            profile = Profile(
                user_id=user.id,
                age=user.age,
                cholesterol=float(form["cholesterol"]),
                heart_rate=health.heart_rate if health else 70,
                diabetes=bool(int(form["diabetes"])),
                family_history=bool(int(form["family_history"])),
                smoking=bool(int(form["smoking"])),
                obesity=bool(int(form["obesity"])),
                alcohol_consumption=bool(int(form["alcohol_consumption"])),
                exercise_hours_per_day=float(form["exercise_hours_per_day"]),
                diet=form["diet"],
                previous_heart_problems=bool(int(form["previous_heart_problems"])),
                medication_use=bool(int(form["medication_use"])),
                stress_level=form["stress_level"],
                sedentary_hours_per_day=float(form["sedentary_hours_per_day"]),
                bmi=user.weight / (user.height ** 2),
                sleep_hours_per_day=float(form["sleep_hours_per_day"]),
                blood_sugar=float(form["blood_sugar"]),
                systolic_blood_pressure=float(form["systolic_blood_pressure"]),
                diastolic_blood_pressure=float(form["diastolic_blood_pressure"]),
                diet_type=form.get("diet_type"),
                allergies=form.get("allergies"),
                photo=photo_filename
            )
            db.add(profile)
            flash("Profile created successfully!", "success")
        else:
            for field in ["cholesterol", "exercise_hours_per_day", "sedentary_hours_per_day",
                          "sleep_hours_per_day", "blood_sugar", "systolic_blood_pressure",
                          "diastolic_blood_pressure"]:
                if form.get(field):
                    setattr(profile, field, float(form[field]))

            for field in ["diabetes", "family_history", "smoking", "obesity", "alcohol_consumption",
                          "previous_heart_problems", "medication_use"]:
                if form.get(field):
                    setattr(profile, field, bool(int(form[field])))

            for field in ["diet", "stress_level", "diet_type", "allergies"]:
                if form.get(field):
                    setattr(profile, field, form[field])

            if user.weight and user.height:
                new_bmi = user.weight / (user.height ** 2)
                if profile.bmi != new_bmi:
                    profile.bmi = new_bmi

            if photo_filename:
                profile.photo = photo_filename

            flash("Profile updated successfully!", "success")

        db.commit()
        db.close()
        return redirect(url_for('home.home'))

    db.close()
    return render_template('profile.html', profile=profile)
