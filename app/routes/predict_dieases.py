import requests
from flask import request, render_template, Blueprint
import pickle

API_URL = "http://127.0.0.1:8000/predict_dieases"
pre_die = Blueprint('predict_dieases', __name__)

with open("pickle_files/Dieases.pkl", "rb") as f:
    _, _, all_symptoms = pickle.load(f)

@pre_die.route("/predict_dieases", methods=["POST", "GET"])
def predict_dieases():
    if request.method == "POST":
        selected_symptoms = request.form.getlist("symptom[]")
        
        input_data = {
            'symptom': selected_symptoms
        }
        try:
            response = requests.post(API_URL, json=input_data)
            if response.status_code == 200:
                result = response.json()
                return render_template("dieases_result.html", predictions=result['top_predictions'])
            else:
                return render_template("dieases_result.html", predictions=response.text)
        except requests.exceptions.ConnectionError:
            return "Could not connect to the FastAPI server"
    return render_template("predict_dieases.html", symptoms=all_symptoms)