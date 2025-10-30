from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from datetime import timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import os
import json

# ================= CONFIG =================
class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///ai.db")
    DEBUG = os.getenv("DEBUG", "True") == "True"
    SECRET_KEY = os.getenv("SECRET_KEY", "your-very-secret-key")

    # ================= GOOGLE OAUTH CONFIG =================
    GOOGLE_CLIENT_SECRET_JSON = os.getenv("GOOGLE_CLIENT_SECRET_JSON")  # Loaded from env on Railway

    if GOOGLE_CLIENT_SECRET_JSON:
        # ✅ Parse JSON from environment variable
        CLIENT_SECRETS_FILE = json.loads(GOOGLE_CLIENT_SECRET_JSON)
        REDIRECT_URI = CLIENT_SECRETS_FILE["web"]["redirect_uris"][0]
    else:
        # ✅ Fallback to local file for local development
        CLIENT_SECRETS_FILE = "client_secret.json"
        REDIRECT_URI = os.getenv(
            "REDIRECT_URI",
            "http://localhost:5000/oauth2callback"
        )

    SCOPES = [
        "https://www.googleapis.com/auth/fitness.activity.read",
        "https://www.googleapis.com/auth/fitness.heart_rate.read",
        "https://www.googleapis.com/auth/fitness.sleep.read",
        "https://www.googleapis.com/auth/fitness.oxygen_saturation.read",
        "https://www.googleapis.com/auth/fitness.body.read"
    ]

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

    start_scheduler()

    @app.route("/flask")
    def health():
        return {"status": "✅ Flask backend running on Railway"}

    # ✅ Optional check route (for debugging on Railway)
    @app.route("/flask/check_env")
    def check_env():
        has_secret = bool(os.getenv("GOOGLE_CLIENT_SECRET_JSON"))
        return {
            "GOOGLE_CLIENT_SECRET_JSON_found": has_secret,
            "redirect_uri": app.config["REDIRECT_URI"]
        }

    return app
