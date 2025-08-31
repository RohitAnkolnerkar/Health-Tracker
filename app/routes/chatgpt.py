from flask import Blueprint, render_template, request, session, redirect, url_for
import requests
import os

cha = Blueprint('Ai', __name__)

HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_MODEL = "google/flan-t5-large"  # More stable model

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
        user_input = request.form["message"]
        session["chat_history"].append({"role": "user", "content": user_input})
        session.modified = True

        full_prompt = build_prompt(session["chat_history"])

        headers = {
            "Authorization": f"Bearer {HF_API_TOKEN}"
        }
        payload = {
            "inputs": full_prompt,
            "parameters": {
                "max_new_tokens": 100,
                "temperature": 0.7
            }
        }

        response = requests.post(
            f"https://api-inference.huggingface.co/models/{HF_MODEL}",
            headers=headers,
            json=payload
        )

        print("Status code:", response.status_code)
        print("Response:", response.text)

        try:
            data = response.json()
            if isinstance(data, dict) and "error" in data:
                reply = f"⚠️ API Error: {data['error']}"
            elif isinstance(data, list) and "generated_text" in data[0]:
                generated = data[0]["generated_text"]
                reply = generated.replace(full_prompt, "").strip()
            else:
                reply = "⚠️ AI did not return a valid response."
        except Exception as e:
            print("Parsing error:", e)
            reply = "❌ Sorry, I couldn't generate a response."

        session["chat_history"].append({"role": "assistant", "content": reply})
        session.modified = True

        return redirect(url_for("Ai.chat"))

    return render_template("chat.html", chat_history=session.get("chat_history", []))

@cha.route("/reset")
def reset():
    session.pop("chat_history", None)
    return redirect(url_for("Ai.chat"))

def build_prompt(history):
    prompt = ""
    for msg in history:
        if msg["role"] == "user":
            prompt += f"User: {msg['content']}\n"
        elif msg["role"] == "assistant":
            prompt += f"AI: {msg['content']}\n"
    prompt += "AI:"
    return prompt
