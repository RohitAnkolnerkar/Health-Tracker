from flask import Blueprint, render_template, request, session, redirect, url_for
import requests
from datetime import datetime
from app.model import User, HealthRecord, Intake, UserGoal, Profile
from app import sessionLocal
from app.utils.recomendation import get_calorie_burn_recommendation
from app.utils.meal_recc import get_spoonacular_meals
from app.utils.diet_plan import generate_diet_plan

inta = Blueprint("Intake", __name__)
FASTAPI_URL = "http://localhost:8000/predict_daily_calories"

@inta.route("/total_intake", methods=["GET", "POST"])
def total():
    prediction = None
    breakdown = []
    recommendation = []
    calorie_burn = 0
    water_input = 0

    if request.method == "POST":
        food_input = request.form["food_items"]
        food_list = [item.strip() for item in food_input.split(",") if item.strip()]
        meal_time = request.form['meal_time']  # ✅ FIXED
        water_input = float(request.form["water_amount"])

        try:
            response = requests.post(FASTAPI_URL, json={"food_list": food_list})
            if response.status_code == 200:
                result = response.json()
                prediction = result["total_calories"]
                breakdown = result["breakdown"]

                if "user" in session:
                    db = sessionLocal()
                    username = session['user'] 
                    user = db.query(User).filter_by(username=username).first()

                    if user:
                        calorie_data = db.query(HealthRecord.calories_burned).filter_by(user_id=user.id).order_by(HealthRecord.created_at.desc()).first()
                        if calorie_data and calorie_data[0] is not None:
                            calorie_burn = calorie_data[0]

                        recommendation = get_calorie_burn_recommendation(
                            calories_burned=calorie_burn,
                            calories_consumed=prediction
                        )

                        intake_record = Intake(
                            user_id=user.id,
                            calorie_intake=prediction,
                            meal_time=datetime.strptime(meal_time, "%Y-%m-%dT%H:%M"),  # Ensure correct format
                            water_intake=water_input
                        )
                        db.add(intake_record)
                        db.commit()
                    else:
                        prediction = "User not found."
                    db.close()
                else:
                    prediction = "User not logged in."
            else:
                prediction = "FastAPI server error."
        except Exception as e:
            prediction = f"Request failed: {e}"

    return render_template("intake.html", prediction=prediction, water_intake=water_input, breakdown=breakdown, recommendation=recommendation)


@inta.route("/meal_recommendations_api")
def meal_recommendations_api():
    db = sessionLocal()
    if "user" not in session:
        return redirect(url_for("register.login"))

    username = session["user"]
    user = db.query(User).filter_by(username=username).first()
    user_goal = db.query(UserGoal).filter_by(user_id=user.id).first()
    profile = db.query(Profile).filter_by(user_id=user.id).first()

    today_entries = db.query(Intake).filter(
        Intake.user_id == user.id,
        Intake.meal_time >= datetime.now().date()
    ).all()

    now = datetime.now()
    hour = now.hour
    meal_type = "breakfast" if hour < 11 else "lunch" if hour < 17 else "dinner"

    consumed = sum([entry.calorie_intake for entry in today_entries if entry.calorie_intake])
    max_calories = user_goal.target_value - consumed if user_goal else None

    spoon_meals = get_spoonacular_meals(
        meal_type=meal_type,
        diet=profile.diet_type if profile else None,
        allergies=profile.allergies.split(",") if profile and profile.allergies else [],
        max_calories=max_calories
    )
    return render_template("recommendations_api.html", meals=spoon_meals)

@inta.route("/diet_plan")
def diet_plan():
    db = sessionLocal()
    if "user" not in session:
        return redirect(url_for("register.login"))

    username = session["user"]
    user = db.query(User).filter_by(username=username).first()

    # ✅ Find only "calories consumed" goal
    calorie_goal = db.query(UserGoal).filter(
        UserGoal.user_id == user.id,
        UserGoal.goal_type.ilike("calories consumed")
    ).first()

    profile = db.query(Profile).filter_by(user_id=user.id).first()

    if not (calorie_goal and profile):
        return "Calorie consumption goal or profile missing"

    # ✅ Generate plan based on calorie consumption target
    plan = generate_diet_plan(
        diet_type=profile.diet_type,
        allergies=profile.allergies.split(",") if profile.allergies else [],
        calorie_target=calorie_goal.target_value
    )

    # Default meal times
    today = datetime.now().date()
    meal_times = {
        "breakfast": datetime.combine(today, datetime.strptime("08:00", "%H:%M").time()),
        "lunch": datetime.combine(today, datetime.strptime("13:00", "%H:%M").time()),
        "snack": datetime.combine(today, datetime.strptime("16:00", "%H:%M").time()),
        "dinner": datetime.combine(today, datetime.strptime("20:00", "%H:%M").time())
    }
    db.close()
    return render_template("diet_plan.html", plan=plan, meal_times=meal_times)

@inta.route("/add_meal_from_plan", methods=["POST"])
def add_meal_from_plan():
    db = sessionLocal()
    if "user" not in session:
        return redirect(url_for("register.login"))


    try:
        user = db.query(User).filter_by(username=session["user"]).first()

        meal_time = request.form["meal_time"]
        meal_type = request.form["meal_type"]
        calories = float(request.form["calories"])

        intake = Intake(
            user_id=user.id,
            calorie_intake=calories,
            meal_time=datetime.strptime(meal_time, "%Y-%m-%d %H:%M:%S"),
            water_intake=0  # or allow form input later
        )
        db.add(intake)
        db.commit()
        db.close()
        return redirect(url_for("Intake.diet_plan"))
    except Exception as e:
        print("Error adding meal:", e)
        return "Error saving meal to intake"
