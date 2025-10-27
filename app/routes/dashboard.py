from flask import Blueprint, jsonify, session, request, render_template, redirect
from datetime import datetime, timedelta
from statistics import mean
import pandas as pd
from app import sessionLocal
from app.model import User, HealthRecord, Intake, Profile, UserGoal
dashboard_api = Blueprint("dashboard_api", __name__)
from app.utils.send_message  import user_reminders 
from app.utils.daily_insights import generate_daily_insights

@dashboard_api.route("/dashboard")
def dashboard_page():
    if "user" not in session:
        return redirect("/login")
    return render_template("dashboard.html")


@dashboard_api.route("/api/dashboard-data")
def api_dashboard_data():
    if "user" not in session:
        return jsonify({"error": "Unauthorized"}, 401)

    db = sessionLocal()
    user = db.query(User).filter(User.username == session["user"]).first()

    days = int(request.args.get("days", 7))
    time_range = datetime.utcnow() - timedelta(days=days)

    records = db.query(HealthRecord).filter(
        HealthRecord.user_id == user.id,
        HealthRecord.created_at >= time_range
    ).order_by(HealthRecord.created_at).all()

    df = pd.DataFrame([{
        "created_at": r.created_at,
        "heart_rate": r.heart_rate,
        "steps": r.steps,
        "calories_burned": r.calories_burned,
        "blood_pressure": r.blood_pressure
    } for r in records])

    insights, alerts, cards = {}, [], []

    if not df.empty:
        df['created_at'] = pd.to_datetime(df['created_at'])
        insights["Avg Heart Rate"] = f"{df.heart_rate.mean():.1f} bpm"
        insights["Avg Steps"] = f"{df.steps.mean():.0f}"
        insights["Avg Calories Burned"] = f"{df.calories_burned.mean():.0f} kcal"

        latest = df.iloc[-1]
        cards.append(f"Heart Rate: {latest.heart_rate} bpm")
        cards.append(f"Steps: {latest.steps}")
        cards.append(f"Calories Burned: {latest.calories_burned} kcal")

        if latest.heart_rate > 90:
            alerts.append(f"⚠️ High Heart Rate: {latest.heart_rate} bpm")

        try:
            sys, dia = map(int, latest.blood_pressure.split("/"))
            if sys > 140 or dia > 90:
                alerts.append(f"⚠️ High Blood Pressure: {latest.blood_pressure}")
        except:
            pass

    intake = db.query(Intake).filter(
        Intake.user_id == user.id,
        Intake.updates_at >= time_range
    ).all()

    if intake:
        insights["Avg Calorie Intake"] = f"{mean([r.calorie_intake for r in intake]):.0f} kcal"
        water_avg = mean([r.water_intake for r in intake])
        insights["Avg Water Intake"] = f"{water_avg:.1f} L"
        if water_avg < 3.0:
            insights["Hydration Tip"] = "💧 Drink more water"

    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if profile:
        insights["Heart Risk"] = "⚠️ High Risk of Heart Attack" if profile.heart_attack_risk_binary else "✅ No immediate heart risk"

    goals = db.query(UserGoal).filter(
        UserGoal.user_id == user.id,
        UserGoal.status == "active"
    ).all()

   
    goal_progress = []
    for g in goals:
      
      pct = (g.current_progress / g.target_value) * 100 if g.target_value else 0
      goal_progress.append({
         "description": f"{g.goal_type.capitalize()} — Target: {g.target_value}",
         "percentage": pct
      })


    heart_data = {
        "labels": df['created_at'].dt.strftime('%Y-%m-%d %H:%M').tolist() if not df.empty else [],
        "values": df['heart_rate'].tolist() if not df.empty else []
    }

    steps_data = {
        "labels": df['created_at'].dt.strftime('%Y-%m-%d %H:%M').tolist() if not df.empty else [],
        "values": df['steps'].tolist() if not df.empty else []
    }
    daily_insight_list = generate_daily_insights(user.id, db)
    

    # Add medication reminders
    reminders = user_reminders.get(user.id, [])
    alerts.extend(reminders)
    user_reminders[user.id] = []  # clear after showing once

    db.close()

    return jsonify({
        "insights": insights,
        "alerts": alerts,
        "cards": cards,
        "heartData": heart_data,
        "stepsData": steps_data,
        "goal": goal_progress,
        "dailyInsights": daily_insight_list
    })
