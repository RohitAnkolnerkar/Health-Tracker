from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.model import HealthRecord, Intake, UserGoal, DailyGoalProgress, User

def percent_change(today_val, yesterday_val):
    if yesterday_val == 0:
        return 100 if today_val > 0 else 0
    return round((today_val - yesterday_val) / yesterday_val * 100, 2)

def generate_daily_insights(user_id: int, db: Session):
    insights = []

    today = date.today()
    yesterday = today - timedelta(days=1)

    user = db.query(User).filter_by(id=user_id).first()

    if not user:
        return ["User not found"]

    # 📊 Health Record Comparison
    today_record = db.query(HealthRecord).filter_by(user_id=user_id).order_by(HealthRecord.created_at.desc()).first()
    yesterday_record = db.query(HealthRecord).filter(HealthRecord.user_id == user_id, HealthRecord.created_at <= yesterday).order_by(HealthRecord.created_at.desc()).first()

    if today_record and yesterday_record:
        step_diff = percent_change(today_record.steps, yesterday_record.steps)
        cal_diff = percent_change(today_record.calories_burned, yesterday_record.calories_burned)
        sleep_diff = today_record.sleep_hours - yesterday_record.sleep_hours

        if step_diff > 10:
            insights.append(f"🚶 You've walked {step_diff}% more than yesterday. Great job!")
        elif step_diff < -10:
            insights.append(f"⚠️ You walked less today — try to hit your goal tomorrow.")

        if cal_diff > 10:
            insights.append(f"🔥 You burned {cal_diff}% more calories today — nice effort!")

        if sleep_diff >= 1:
            insights.append(f"😴 You slept {sleep_diff:.1f} more hours than yesterday — well done.")
        elif sleep_diff <= -1:
            insights.append(f"🔻 You slept less today. Try to get 7–8 hours of sleep.")

    # 💧 Intake Comparison
    today_intake = db.query(Intake).filter(Intake.user_id == user_id).order_by(Intake.updates_at.desc()).first()
    yesterday_intake = db.query(Intake).filter(Intake.user_id == user_id, Intake.updates_at <= yesterday).order_by(Intake.updates_at.desc()).first()

    if today_intake and yesterday_intake:
        water_diff = percent_change(today_intake.water_intake, yesterday_intake.water_intake)
        cal_intake_diff = percent_change(today_intake.calorie_intake, yesterday_intake.calorie_intake)

        if water_diff < 0:
            insights.append("💧 Water intake is lower today. Stay hydrated — aim for 2.5L+.")
        elif water_diff > 0:
            insights.append(f"✅ You drank {water_diff}% more water today. Great hydration!")

        if cal_intake_diff > 10:
            insights.append(f"🍽️ You consumed {cal_intake_diff}% more calories than yesterday.")
        elif cal_intake_diff < -10:
            insights.append(f"📉 You ate lighter today — good if you’re aiming for weight loss.")

    # 🎯 Goal Progress (for today)
    today_goals = db.query(UserGoal).filter_by(user_id=user_id, status='active').all()
    for goal in today_goals:
        progress_record = db.query(DailyGoalProgress).filter_by(user_goal_id=goal.id, date=today).first()
        if progress_record:
            progress = progress_record.progress
            percent = (progress / goal.target_value) * 100 if goal.target_value > 0 else 0
            if percent >= 100:
                insights.append(f"🏆 You completed your goal: {goal.goal_type}!")
            elif percent >= 75:
                insights.append(f"🎯 Almost there on your {goal.goal_type} goal ({percent:.0f}%) — push a bit more!")

    if not insights:
        insights.append("No new insights today. Keep tracking your health!")

    return insights
