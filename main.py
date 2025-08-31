from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Literal, Annotated, List
import pickle
import pandas as pd

# === Load Models ===
with open("pickle_files/heart_attack_risk_model.pkl", 'rb') as f:
    heart_model = pickle.load(f)

with open("pickle_files/calorie_model.pkl", 'rb') as f:
    calorie_model = pickle.load(f)

with open("pickle_files/Dieases.pkl", "rb") as f:
    disease_model, le, all_symptom = pickle.load(f)

with open("pickle_files/intake.pkl",'rb') as f:
    intake_model=pickle.load(f)   

# === Initialize App ===
fastapi_app = FastAPI(title="AI Health Tracker API", version="1.0")

# === Heart Attack Schema ===
class HeartAttackInput(BaseModel):
    Age: int
    Gender: Literal["M", "F"]
    BMI: float
    Systolic_blood_pressure: int = Field(..., alias="Systolic blood pressure")
    Diastolic_blood_pressure: int = Field(..., alias="Diastolic blood pressure")
    Cholesterol: int
    Blood_sugar: int = Field(..., alias="Blood sugar")
    Heart_rate: int = Field(..., alias="Heart rate")
    Previous_Heart_Problems: Literal["Yes", "No"] = Field(..., alias="Previous Heart Problems")
    Family_History: Literal["Yes", "No"] = Field(..., alias="Family History")
    Smoking: Literal["Yes", "No"]
    Alcohol_Consumption: Literal["Never", "Occasional", "Regular"]
    Diabetes: Literal["Yes", "No"]
    Exercise_Hours_Per_Week: float = Field(..., alias="Exercise Hours Per Week")
    Sedentary_Hours_Per_Day: float = Field(..., alias="Sedentary Hours Per Day")
    Diet: Literal["Healthy", "Unhealthy"]
    Sleep_Hours_Per_Day: float = Field(..., alias="Sleep Hours Per Day")
    Stress_Level: Literal["Low", "Moderate", "High"]
    Medication_Use: Literal["Yes", "No"]
    

# === Calorie Prediction Schema ===
class Caloriesinput(BaseModel):
    Gender: Annotated[Literal['male', 'female'], Field(..., description="Gender")]
    Age: Annotated[int, Field(..., description="Enter your Age")]
    Height: Annotated[float, Field(..., gt=0, description="Enter your Height in meters")]
    Weight: Annotated[float, Field(..., gt=0, description="Enter your Weight in kg")]
    Duration: Annotated[float, Field(..., gt=0, description="Exercise Duration in Minutes")]
    Heart_Rate: Annotated[int, Field(..., gt=40, description="Heart Rate per Minute")]
    Body_Temp: Annotated[float, Field(..., gt=30, description="Body Temperature in Celsius")]

    @computed_field
    def Bmi(self) -> float:
        return self.Weight / (self.Height ** 2)

# === Disease Prediction Schema ===
class Userinput(BaseModel):
    symptom: List[str]

# === Routes ===

@fastapi_app.get("/", tags=["Root"])
def root():
    return {"status": "✅ FastAPI is running"}

@fastapi_app.post("/predict_heart_attack_risk", tags=["Heart Attack Prediction"])
def predict_heart_attack(data: HeartAttackInput):
    df = pd.DataFrame([data.model_dump(by_alias=True)])
    prediction = heart_model.predict(df)[0]
    probability = heart_model.predict_proba(df)[0][1]
    return JSONResponse(
        status_code=200,
        content={
            "heart_attack_risk": bool(prediction),
            "risk_probability": round(probability, 4)
        }
    )

@fastapi_app.post("/predict_calories", tags=["Calorie Prediction"])
def predict_calories(data: Caloriesinput):
    input_df = pd.DataFrame([{
        'Gender': data.Gender,
        'Age': data.Age,
        'Height': data.Height,
        'Weight': data.Weight,
        'Duration': data.Duration,
        'Heart_Rate': data.Heart_Rate,
        'Body_Temp': data.Body_Temp,
        'Bmi': data.Bmi
    }])
    prediction = calorie_model.predict(input_df)[0]
    return JSONResponse(status_code=200, content={'predicted_calories': prediction})

@fastapi_app.post("/predict_dieases", tags=["Disease Prediction"])
def predict_diseases(data: Userinput):
    selected_symptoms = [symptom.strip().lower().replace(" ", "_") for symptom in data.symptom]
    input_vector = [1 if symptom in selected_symptoms else 0 for symptom in all_symptom]
    input_df = pd.DataFrame([input_vector], columns=all_symptom)

    probs = disease_model.predict_proba(input_df)[0]
    top_indices = probs.argsort()[-3:][::-1]
    top_diseases = le.inverse_transform(top_indices)
    top_probs = [round(probs[i] * 100, 2) for i in top_indices]

    result = [{"disease": d, "confidence": p} for d, p in zip(top_diseases, top_probs)]
    
    print("Returned result:", result)  # <-- For debugging
    return JSONResponse(status_code=200, content={"top_predictions": result})




class FoodItems(BaseModel):
    food_list: list[str]

@fastapi_app.post("/predict_daily_calories")
def predict_daily_calories(items: FoodItems):
    results = []
    total = 0.0
    print("Received items:", items.food_list)
    for food in items.food_list:
        food_cleaned = food.strip().lower()
        prediction = intake_model.predict([food_cleaned])[0]
        cal = round(prediction, 2)
        results.append({"food_item": food, "calories": cal})
        total += cal

    return JSONResponse(status_code=200, content={
        "total_calories": round(total, 2),
        "breakdown": results
    })