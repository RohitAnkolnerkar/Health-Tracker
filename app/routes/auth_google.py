import os
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
from flask import Blueprint, session, redirect, url_for, current_app, request
from google_auth_oauthlib.flow import Flow
import json
from app import sessionLocal
from app.model import User

auth_google = Blueprint("auth_google", __name__)

@auth_google.route("/authorize")
def authorize():
    flow = Flow.from_client_secrets_file(
        current_app.config["CLIENT_SECRETS_FILE"],
        scopes=current_app.config["SCOPES"],
        redirect_uri=current_app.config["REDIRECT_URI"]
    )
    auth_url, state = flow.authorization_url(
        prompt='consent',
        include_granted_scopes='true'
    )
    session["flow_state"] = state  # ✅ fixed: use returned state, not flow.state
    return redirect(auth_url)

@auth_google.route("/oauth2callback")
def oauth2callback():
    from google_auth_oauthlib.flow import Flow

    flow = Flow.from_client_secrets_file(
        current_app.config["CLIENT_SECRETS_FILE"],
        scopes=current_app.config["SCOPES"],
        redirect_uri=current_app.config["REDIRECT_URI"]
    )
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials

    username = session.get("user")
    if not username:
        print("⚠️ Session expired. No user in session.")
        return redirect("/login")  # Or redirect to your login page

    db = sessionLocal()
    user = db.query(User).filter_by(username=username).first()

    if user:
        user.google_token = credentials.to_json()
        db.commit()
        print(f"✅ Google Fit token saved for {username}")
        return redirect(url_for("direct.fetch_and_store_fit_data"))
    else:
        return "User not found", 404
