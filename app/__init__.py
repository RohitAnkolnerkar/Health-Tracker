# app/__init__.py
from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from datetime import timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import os

# ================= CONFIG =================
class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///ai.db")
    DEBUG = os.getenv("DEBUG", "True") == "True"
    SECRET_KEY = os.getenv("SECRET_KEY", "your-very-secret-key")
    CLIENT_SECRETS_FILE = "client_secret.json"
    SCOPES = [
        "https://www.googleapis.com/auth/fitness.activity.read",
        "https://www.googleapis.com/auth/fitness.heart_rate.read",
        "https://www.googleapis.com/auth/fitness.sleep.read",
        "https://www.googleapis.com/auth/fitness.oxygen_saturation.read",
        "https://www.googleapis.com/auth/fitness.body.read"
    ]
    REDIRECT_URI = os.getenv("REDIRECT_URI", "https://your-railway-app-url.up.railway.app/flask/oauth2callback")

# ================= DATABASE SETUP =================
engine = None
sessionLocal = scoped_session(sessionmaker())
Base = declarative_base()


def create_app(config_class=Config):
    app = Flask(__name__, template_folder='Templates', static_folder='static')
    app.config.from_object(config_class)
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30)

    global engine
    engine = create_engine(app.config["DATABASE_URL"], echo=app.config["DEBUG"])
    sessionLocal.configure(bind=engine)

    from app import model
    with app.app_context():
        Base.metadata.create_all(bind=engine)

    # ================= REGISTER ROUTES =================
    from app.routes.register import auth_bp
    from app.routes.predict_calorie import pre
    from app.routes.predict_dieases import pre_die
    from app.routes.home import ho
    from app.routes.health_records import heal
    from app.routes.Prescription import prescription_bp
    from app.routes.Admin import admin_bp
    from app.routes.goals import gol
    from app.routes.auth_google import auth_google
    from app.routes.live import dir, fetch_all_users_fit_data
    from app.routes.profile import pro
    from app.routes.chatgpt import cha
    from app.routes.predict_intake import inta
    from app.routes.dashboard import dashboard_api
    from app.routes.add_medi import me

    app.register_blueprint(auth_google)
    app.register_blueprint(dir)
    app.register_blueprint(auth_bp)
    app.register_blueprint(pre)
    app.register_blueprint(pre_die)
    app.register_blueprint(ho)
    app.register_blueprint(heal)
    app.register_blueprint(prescription_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(gol)
    app.register_blueprint(pro)
    app.register_blueprint(cha)
    app.register_blueprint(inta)
    app.register_blueprint(dashboard_api)
    app.register_blueprint(me)

    # ================= BACKGROUND JOBS =================
    from app.routes.predict_heartattack import run_heart_risk_batch_prediction
    from app.routes.goals import update_user_goals
    from app.utils.send_message import send_medication_reminders

    def start_scheduler():
        """Run background tasks every few minutes on Railway."""
        scheduler = BackgroundScheduler()
        scheduler.add_job(fetch_all_users_fit_data, "interval", minutes=5)
        scheduler.add_job(run_heart_risk_batch_prediction, "interval", days=1)
        scheduler.add_job(update_user_goals, "interval", minutes=5)
        scheduler.add_job(send_medication_reminders, "interval", minutes=1)
        scheduler.start()
        print("🕒 Background scheduler started successfully (Railway).")

    # Start scheduler on app creation
    start_scheduler()

    @app.route("/flask")
    def health():
        return {"status": "✅ Flask backend running on Railway"}

    return app
