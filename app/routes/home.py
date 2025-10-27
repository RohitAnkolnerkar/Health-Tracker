from flask import request, render_template, Blueprint, redirect, session
from app import sessionLocal
from app.model import User, Profile

ho = Blueprint('home', __name__)
import pandas as pd

@ho.route("/")
def home():
    db = sessionLocal()
    user_photo = None

    if "user" in session:
        username = session["user"]
        user = db.query(User).filter_by(username=username).first()
        if user:
            profile = db.query(Profile).filter_by(user_id=user.id).first()
            if profile and profile.photo:
                user_photo = profile.photo
    db.close()
    return render_template("home.html", user_photo=user_photo)

@ho.route("/goal_home")
def goal_home():
    return render_template("goal_home.html")
