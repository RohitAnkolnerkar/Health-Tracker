from flask import Flask,render_template,url_for
from datetime import datetime
from app import sessionLocal
from app.model import Alert

def alert(user_id, message):
    db = sessionLocal()
    try:
        new_alert = Alert(
            user_id=user_id,
            message=message,
            created_at=datetime.utcnow()
        )
        db.add(new_alert)
        db.commit()
        print(f"🚨 Alert saved for user {user_id}: {message}")
        return render_template("alert.html",alerts=new_alert)
    except Exception as e:
        print(f"❌ Failed to create alert: {e}")
    finally:
        db.close()