from flask import Blueprint, request, render_template, redirect, url_for, session,flash
from datetime import datetime
from app.model import User, Medication
from app import sessionLocal

me = Blueprint("med", __name__)

@me.route("/add_medication", methods=["GET", "POST"])
def add_medication():
    db = sessionLocal()

    if "user" not in session:
        return redirect(url_for("register.login"))

    if request.method == "POST":
        user = db.query(User).filter_by(username=session["user"]).first()

        name = request.form["name"]
        dosage = request.form["dosage"]
        time_str = request.form["time"]  #

    
        start_date_str = request.form["start_date"]  
        end_date_str = request.form["end_date"]      

     
        time_obj = datetime.strptime(time_str, "%I:%M %p").time()
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        print("start_date:", start_date, type(start_date))
        print("end_date:", end_date, type(end_date))

        new_med = Medication(
            user_id=user.id,
            name=name,
            dosage=dosage,
            time=time_obj,
            start_date=start_date,
            end_date=end_date,
            taken_today=False
        )
        db.add(new_med)
        db.commit()
        db.close()
        flash("medication added successfully")
        return redirect(url_for("med.my_medications"))

    return render_template("medication.html")

@me.route("/my_medications")
def my_medications():
    db = sessionLocal()

    if "user" not in session:
        return redirect(url_for("register.login"))

    user = db.query(User).filter_by(username=session["user"]).first()
    if not user:
        db.close()
        return redirect(url_for("register.login"))

    medications = db.query(Medication).filter_by(user_id=user.id).order_by(Medication.start_date.desc()).all()
    db.close()

    return render_template("show_medication.html", medications=medications, username=user.username)

@me.route("/delete_medication/<int:med_id>", methods=["POST"])
def delete_medication(med_id):
    db = sessionLocal()
    if "user" not in session:
        return redirect(url_for("auth.login"))

    user = db.query(User).filter_by(username=session["user"]).first()
    med = db.query(Medication).filter_by(id=med_id, user_id=user.id).first()

    if med:
        db.delete(med)
        db.commit()

    db.close()
    return redirect(url_for("med.my_medications"))