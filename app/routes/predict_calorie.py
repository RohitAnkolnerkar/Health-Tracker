import requests
from flask import request, render_template, Blueprint,session
from app import sessionLocal
from app.model import User,HealthRecord
from sqlalchemy import desc

API_URL = "http://127.0.0.1:8000/predict_calories"
pre = Blueprint('predict_calorie', __name__)


result=0


@pre.route("/predict_calorie", methods=["POST", "GET"])
def predict_calorie():
    db = sessionLocal()
    if request.method == 'POST':
        username = session['user']
        user = db.query(User).filter_by(username=username).first()
        record = db.query(HealthRecord).filter_by(user_id=user.id).order_by(desc(HealthRecord.created_at)).first()

        input_data = {
            'Gender': user.gender.lower(),
            'Age': int(user.age),
            'Height': user.height,
            'Weight': user.weight,
            'Duration': request.form.get("Duration"),
            'Heart_Rate': record.heart_rate,
            'Body_Temp': request.form.get("Body_Temp")
        }

        try:
            response = requests.post(API_URL, json=input_data)
            if response.status_code == 200:
                result = response.json()
                return render_template("calorie_result.html", prediction=result)
            else:
                return render_template("calorie_result.html", prediction=response.text)
        except requests.exceptions.ConnectionError:
            return "Could not connect to the FastAPI server"
    return render_template("predict_calorie.html")
