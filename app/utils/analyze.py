from app import sessionLocal
from datetime import datetime, timedelta
from statistics import mean

from app.model import User, HealthRecord, Intake, Profile, UserGoal,session

def get_health_insights():
    insights = {}
    db=sessionLocal()
    if 'user' in session:
        username=session['user']
        user=db.query(User).filter(username=username).first()
        last_week = datetime.utcnow() - timedelta(days=7)
        records = db.query(HealthRecord).filter(

            HealthRecord.user_id ==user.id,
            HealthRecord.created_at >= last_week
        ).all()

    if records:
        avg_heart_rate = mean([r.heart_rate for r in records])
        avg_sleep = mean([r.sleep_hours for r in records])
        avg_steps = mean([r.steps for r in records])
        avg_calories_burned = mean([r.calories_burned for r in records])

        insights["heart_rate"] = f"Avg Heart Rate (last 7 days): {avg_heart_rate:.1f} bpm"
        insights["sleep"] = f"Avg Sleep: {avg_sleep:.1f} hrs"
        insights["steps"] = f"Avg Daily Steps: {avg_steps:.0f}"
        insights["calories_burned"] = f"Avg Calories Burned: {avg_calories_burned:.0f} kcal"

        if avg_heart_rate > 100:
            insights["heart_tip"] = "Your heart rate is higher than normal. Consider reducing stress and increasing rest."

    # Intake Data
    intake = db.query(Intake).filter(Intake.user_id ==user.id).order_by(Intake.updates_at.desc()).first()
    if intake:
        avg_calories_intake = mean([r.calorie_intake for r in intake])
        avg_water_intake = mean([r.water_intake for r in intake])
        insights["calorie_intake"] = f"Last Calorie Intake: {avg_calories_intake} kcal"
        insights["water_intake"] = f"Last Water Intake: {avg_water_intake:.1f} L"

        if avg_water_intake < 3.0:
            insights["water_tip"] = "Increase your water intake for better hydration."

    # Profile / Heart Risk
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if profile:
        if profile.heart_attack_risk_binary:
            insights["heart_risk"] = "⚠️ High Risk of Heart Attack. Please consult a cardiologist."
        else:
            insights["heart_risk"] = "✅ No immediate heart attack risk detected."

    # Goals Progress
    goals = db.query(UserGoal).filter(
        UserGoal.user_id == user.id,
        UserGoal.status == "active"
    ).all()

    if goals:
        goal_list = []
        for g in goals:
            progress_pct = (g.current_progress / g.target_value) * 100 if g.target_value > 0 else 0
            goal_list.append(f"{g.goal_type.capitalize()}: {progress_pct:.1f}% completed")

        insights["goals"] = "Your Current Goals:\n" + "\n".join(goal_list)

    return insights
