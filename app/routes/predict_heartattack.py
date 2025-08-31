import requests
from app.model import Profile, User
from app import sessionLocal

API_URL = "http://127.0.0.1:8000/predict_dieases"

def run_heart_risk_batch_prediction():
    db = sessionLocal()
    users = db.query(User).all()

    for user in users:
        profile = db.query(Profile).filter_by(user_id=user.id).order_by(Profile.id.desc()).first()
        if not profile:
            continue

        profile_data = {
            "age": profile.age,
            "cholesterol": profile.cholesterol,
            "heart_rate": profile.heart_rate,
            "diabetes": profile.diabetes,
            "family_history": profile.family_history,
            "smoking": profile.smoking,
            "obesity": profile.obesity,
            "alcohol_consumption": profile.alcohol_consumption,
            "exercise_hours_per_week": profile.exercise_hours_per_week,
            "diet": profile.diet,
            "previous_heart_problems": profile.previous_heart_problems,
            "medication_use": profile.medication_use,
            "stress_level": profile.stress_level,
            "sedentary_hours_per_day": profile.sedentary_hours_per_day,
            "bmi": profile.bmi,
            "sleep_hours_per_day": profile.sleep_hours_per_day,
            "blood_sugar": profile.blood_sugar,
            "systolic_blood_pressure": profile.systolic_blood_pressure,
            "diastolic_blood_pressure": profile.diastolic_blood_pressure
        }

        try:
            response = requests.post(API_URL, json=profile_data)
            if response.status_code == 200:
                result = response.json()
                prediction = result.get("heart_attack_risk")
                profile.heart_attack_risk_binary = prediction
                db.commit()
            else:
                print(f"[ERROR] Prediction failed for user {user.username}: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Connection failed for user {user.username}: {e}")
    
    db.close()
