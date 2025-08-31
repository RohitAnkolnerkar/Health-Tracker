# ✅ Fixed live.py (with better time range, no hardcoded dataSourceId, debug prints)

import json
import requests
from flask import Blueprint, current_app, session, redirect, request, flash, url_for
from google.oauth2.credentials import Credentials
from datetime import datetime
from app import sessionLocal
from app.model import User, HealthRecord
from app.routes.alert import alert


# Blueprint
dir = Blueprint("direct", __name__)

@dir.route("/fetch_fit_data")
def fetch_and_store_fit_data():
    if 'user' not in session:
        print("No user in session.")
        return redirect("/login")

    username = session['user']
    db = sessionLocal()
    user = db.query(User).filter_by(username=username).first()

    if not user:
        print("User not found in database.")
        return "User not found.", 404

    if not user.google_token:
        print("No Google token found for user. Redirecting to authorize.")
        return redirect("/authorize")

    try:
        credentials_info = json.loads(user.google_token)
        credentials = Credentials.from_authorized_user_info(credentials_info)
    except Exception as e:
        print("Error loading credentials:", str(e))
        return redirect("/authorize")

    _fetch_and_store_for_user(user)
    flash("Health data successfully fetched and stored.")
    return redirect(url_for("home.home"))


# 🔁 Background cron job handler

def fetch_all_users_fit_data():
    print("⏳ Background scheduler running...")
    db = sessionLocal()
    users = db.query(User).filter(User.google_token != None).all()

    for user in users:
        try:
            _fetch_and_store_for_user(user)
            print(f"✅ Health data updated for {user.username}")
        except Exception as e:
            print(f"❌ Failed to fetch data for {user.username}: {e}")

    db.commit()


# 🧠 Actual logic to call Fit API and save

def _fetch_and_store_for_user(user):
    credentials_info = json.loads(user.google_token)
    credentials = Credentials.from_authorized_user_info(credentials_info)
    headers = {'Authorization': f'Bearer {credentials.token}'}

    now = int(datetime.now().timestamp() * 1000)
    start = now - (24 * 60 * 60 * 1000)  # ⏱ Last 24 hours

    body = {
        "aggregateBy": [
            {"dataTypeName": "com.google.step_count.delta"},
            {"dataTypeName": "com.google.heart_rate.bpm"}
        ],
        "bucketByTime": {"durationMillis": 300000},
        "startTimeMillis": start,
        "endTimeMillis": now
    }

    url = 'https://www.googleapis.com/fitness/v1/users/me/dataset:aggregate'
    response = requests.post(url, headers=headers, json=body)

    if response.status_code != 200:
        raise Exception(f"Google Fit API error: {response.text}")

    data = response.json()
    print("🔍 Full Fit Response:", json.dumps(data, indent=2))

    steps = 0
    heart_rate = None

    for bucket in data.get('bucket', []):
        for dataset in bucket.get('dataset', []):
            for point in dataset.get('point', []):
                data_type = dataset.get('dataSourceId', '')
                if 'step_count' in data_type:
                    steps += point['value'][0].get('intVal', 0)
                elif 'heart_rate' in data_type:
                    heart_rate = point['value'][0].get('fpVal', None)

    print("💡 Steps:", steps)
    print("💡 Heart Rate:", heart_rate)
    health = HealthRecord(
        user_id=user.id,
        steps=steps,
        heart_rate=int(heart_rate) if heart_rate else None,
        calories_burned=int(steps * 0.045),
        blood_pressure="150/90",
        stress_level="Moderate",
        oxygen_saturation=98,
        sleep_hours=6.5
    )
    db = sessionLocal()
    db.add(health)
    db.commit()
    try:
       
       high_hr = health.heart_rate > 90 if health.heart_rate is not None else False

       bp = health.blood_pressure.split("/")
       high_bp = len(bp) == 2 and (int(bp[0]) > 140 or int(bp[1]) > 90)

       if high_hr or high_bp:
          
          alert_msg = ""
          if high_hr:
             
             alert_msg += f"⚠️ High Heart Rate: {health.heart_rate} bpm. "
          if high_bp:
             alert_msg += f"⚠️ High Blood Pressure: {health.blood_pressure}."

          alert(user.id, alert_msg)
          print("🚨 Alert triggered:", alert_msg)
       else:
          
          print("✅ No alert needed.")
    except Exception as e:
       
       print("⚠️ Failed to trigger alert:", str(e))
