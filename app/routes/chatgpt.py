from flask import Blueprint, render_template, request, session, redirect, url_for
import requests, os, json
from dotenv import load_dotenv
load_dotenv()
cha = Blueprint('Ai', __name__)

# === GEMINI CONFIG ===
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1/models/{GEMINI_MODEL}:generateContent"

# === ROUTES ===
@cha.route("/")
def index():
    return redirect(url_for("Ai.chat"))

@cha.route("/chat_ai", methods=["GET", "POST"])
def chat():
    if "user" not in session:
        session["user"] = "test_user"
    if "chat_history" not in session:
        session["chat_history"] = []

    if request.method == "POST":
        user_input = request.form.get("message", "").strip()
        if not user_input:
            return redirect(url_for("Ai.chat"))

        session["chat_history"].append({"role": "user", "content": user_input})
        session.modified = True

        # Prepare payload for Gemini
        prompt_text = "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in session["chat_history"]])
        payload = {"contents": [{"parts": [{"text": prompt_text}]}]}

        try:
            response = requests.post(
                f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
                headers={"Content-Type": "application/json"},
                json=payload
            )
            data = response.json()
            if response.status_code == 200 and "candidates" in data and len(data["candidates"]) > 0:
                reply = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            else:
                reply = "⚠️ No valid response from AI."
        except Exception as e:
            print("Error:", e)
            reply = "❌ Could not connect to Gemini AI."

        session["chat_history"].append({"role": "assistant", "content": reply})
        session.modified = True

        return redirect(url_for("Ai.chat"))

    return render_template("chat.html", chat_history=session.get("chat_history", []))

@cha.route("/reset")
def reset():
    session.pop("chat_history", None)
    return redirect(url_for("Ai.chat"))
