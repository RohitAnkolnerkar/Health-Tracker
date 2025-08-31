from flask import request, jsonify,Blueprint,render_template,session,url_for,redirect,flash  
from app import sessionLocal
from app.model import UserGoal,User,HealthRecord,DailyGoalProgress,Intake
from datetime import date
from datetime import timedelta
from sqlalchemy.sql import func
from datetime import date, timedelta
from sqlalchemy.orm import joinedload
def update_user_goals():
    db = sessionLocal()
    
    if "user" not in session:
        return redirect(url_for("register.login"))  # Redirect to login if not logged in

    username = session["user"]
    user = db.query(User).filter_by(username=username).first()

    if not user:
        return "User not found", 404

    # Get latest health record
    latest = db.query(HealthRecord).filter_by(user_id=user.id).order_by(HealthRecord.created_at.desc()).first()
    if not latest:
        return "No health records found", 404

    today = date.today()

    for goal in db.query(UserGoal).options(joinedload(UserGoal.daily_progress)).filter_by(user_id=user.id).all():
        value = None

        if goal.goal_type.lower() == "steps":
            value = latest.steps
        elif goal.goal_type.lower() == "calories burned":
            value = latest.calories_burned
        elif goal.goal_type.lower() == "sleep":
            value = latest.sleep_hours
        elif goal.goal_type.lower() == "heart rate":
            value = latest.heart_rate

        elif goal.goal_type.lower() == "calories consumed":
          
          latest_intake = db.query(Intake).filter_by(user_id=user.id).order_by(Intake.meal_time.desc()).first()
          value = latest_intake.calorie_intake if latest_intake else 0

        
    
        # Add more goal_type conditions if needed

        if value is not None:
            # Check if progress entry for today exists
            existing_progress = next((p for p in goal.daily_progress if p.date == today), None)

            if existing_progress:
                existing_progress.progress = value
            else:
                new_progress = DailyGoalProgress(user_goal_id=goal.id, date=today, progress=value)
                db.add(new_progress)

            
            total_progress = sum(p.progress for p in goal.daily_progress if p.date <= today)
            goal.current_progress = total_progress

    db.commit()
    db.close()



def get_goal_streak(goal):
    today = date.today()
    streak = 0
    max_streak = 0
    current = 0
    dates = set([dp.date for dp in goal.daily_progress])

    # Go back from today to the start date
    current_date = today
    while current_date >= goal.start_date.date():
        if current_date in dates:
            current += 1
            streak = max(streak, current)
        else:
            current = 0
        current_date -= timedelta(days=1)

    return streak    





gol=Blueprint("goals",__name__)

@gol.route('/goals', methods=['GET', 'POST'])
def create_goal():
    if 'user' not in session:
        return redirect(url_for('register.login')) 

    db = sessionLocal()
    username = session['user']
    user = db.query(User).filter_by(username=username).first()

    if not user:
        db.close()
        return "User not found", 404

    if request.method == "POST":
        form = request.form
        
        goal = UserGoal(
            user_id=user.id, 
            goal_type=form['goal_type'],
            target_value=form['target_value'],
            unit=form['unit'],
            frequency=form.get('frequency', 'daily'),
            start_date=date.fromisoformat(form['start_date']),
            end_date=date.fromisoformat(form['end_date']),
        )
        db.add(goal)
        db.commit()
        db.close()
        return redirect(url_for('goals.get_goals'))  # or any page you want

    db.close()
    return render_template("create_goals.html")



@gol.route('/show_goals', methods=['GET'])
def get_goals():
    if 'user' in session:
        username = session['user']
        db_session = sessionLocal()

        try:
            user = db_session.query(User).filter_by(username=username).first()
            if not user:
                return "User not found", 404

            goals = db_session.query(UserGoal).filter_by(user_id=user.id).all()
            goals_with_streak = []

            for goal in goals:
                streak = get_goal_streak(goal)  # ✅ You must have this function defined
                progress_by_date = {
                    dp.date.isoformat(): dp.progress for dp in goal.daily_progress
                }
                goals_with_streak.append({
                    "goal": goal,
                    "streak": streak,
                    "progress_by_date": progress_by_date
                })

            return render_template(
                'goals.html',
                username=user.username,
                goals=goals_with_streak,
                today=date.today(),
                timedelta=timedelta  
            )

        finally:
            db_session.close()

   


@gol.route('/dashboard/<int:user_id>')
def dashboard():
    if 'user'  in session:
       db=sessionLocal()
       username=session['user']
       user=db.query(User).filter_by(username=username).first()
       goals = db.query(UserGoal).filter_by(user_id=user.id).all()
       suggested_goal = redirect("goals.suggest_goals()")
       return render_template('dashboard.html', username=f"User {user.id}", goals=goals, suggested_goal=suggested_goal)



@gol.route('/goal_suggestions', methods=['GET'])
def suggest_goals():
    if 'user'  in session:

        username=session['user']
        db=sessionLocal()
        today = date.today()
        past_date = today - timedelta(days=7)
        user=db.query(User).filter_by(username=username).first()
        

    # Aggregate past 7 days of data
        result = db.query(
           
           func.avg(HealthRecord.steps).label("avg_steps"),
           func.avg(HealthRecord.sleep_hours).label("avg_sleep"),
           func.avg(HealthRecord.calories_burned).label("avg_calories")).filter(
           HealthRecord.user_id == user.id,
           HealthRecord.created_at.between(past_date, today) ).first()
        suggestions = []

        if result.avg_steps:
          
          
          steps_target = min(int(result.avg_steps * 1.1), 12000)
          suggestions.append({
             
            "goal_type": "steps",
            "suggested_target": steps_target,
            "unit": "steps",
            "reason": "10% increase over your weekly average"
        })

        if result.avg_sleep:
         
         
         if result.avg_sleep < 6.5:

            sleep_target = 7
         elif result.avg_sleep > 8.5:
            sleep_target = 8
         else:
            sleep_target = round(result.avg_sleep, 1)

         suggestions.append({

            "goal_type": "sleep",
            "suggested_target": sleep_target,
            "unit": "hours",
            "reason": "Improved sleep consistency"
        })

        if result.avg_calories:
         
         calories_target = round(result.avg_calories * 0.95, 0)
         suggestions.append({

            "goal_type": "calories",
            "suggested_target": calories_target,
            "unit": "kcal",
            "reason": "5% reduction to support weight control"
        })
        db.close()
         

    return jsonify({"suggestions": suggestions})



