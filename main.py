# main.py
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Literal, Annotated, List
import pickle
import pandas as pd
import os
import gdown

# === Paths & Config ===
MODEL_DIR = "pickle_files"
os.makedirs(MODEL_DIR, exist_ok=True)

HEART_MODEL_PATH = os.path.join(MODEL_DIR, "heart_attack_risk_model.pkl")
CALORIE_MODEL_PATH = os.path.join(MODEL_DIR, "calorie_model.pkl")
DISEASE_MODEL_PATH = os.path.join(MODEL_DIR, "Dieases.pkl")
INTAKE_MODEL_PATH = os.path.join(MODEL_DIR, "intake.pkl")

GOOGLE_DRIVE_ID = "1gBWILwHtY0v0Jad6ZF-TjwdX6ETprkz9"
GOOGLE_DRIVE_URL = f"https://drive.google.com/uc?id={GOOGLE_DRIVE_ID}"

# === Model Globals ===
heart_model = None
calorie_model = None
disease_model = None
le = None
all_symptom = None
intake_model = None


def download_intake_model():
    """Download intake.pkl from Google Drive if missing."""
    if not os.path.exists(INTAKE_MODEL_PATH):
        print("⬇️ Downloading intake.pkl from Google Drive...")
        try:
            gdown.download(GOOGLE_DRIVE_URL, INTAKE_MODEL_PATH, quiet=False)
            print("✅ intake.pkl downloaded successfully.")
        except Exception as e:
            print(f"❌ intake.pkl download failed: {e}")
    else:
        print("✅ intake.pkl already exists. Skipping download.")


def load_models():
    """Load all models sequentially (memory-safe)."""
    global heart_model, calorie_model, disease_model, le, all_symptom
    try:
        print("🔄 Loading models...")
        with open(HEART_MODEL_PATH, "rb") as f:
            heart_model = pickle.load(f)
        with open(CALORIE_MODEL_PATH, "rb") as f:
            calorie_model = pickle.load(f)
        with open(DISEASE_MODEL_PATH, "rb") as f:
            disease_model, le, all_symptom = pickle.load(f)
        print("✅ Models loaded successfully.")
    except Exception as e:
        print(f"❌ Model loading error: {e}")


def load_intake_model():
    """Lazily load the intake model only when needed."""
    global intake_model
    if intake_model is None:
        download_intake_model()
        try:
            with open(INTAKE_MODEL_PATH, "rb") as f:
                intake_model = pickle.load(f)
            print("✅ intake.pkl loaded successfully.")
        except Exception as e:
            print(f"❌ intake.pkl load failed: {e}")


# === Initialize FastAPI App ===
fastapi_app = FastAPI(title="AI Health Tracker API", version="1.2.0")


@fastapi_app.on_event("startup")
def on_startup():
    print("🚀 Starting FastAPI app — loading minimal models...")
    load_models()


# === Input Schemas ===
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


class Caloriesinput(BaseModel):
    Gender: Annotated[Literal['male', 'female'], Field(...)]
    Age: int
    Height: float
    Weight: float
    Duration: float
    Heart_Rate: int
    Body_Temp: float

    @computed_field
    def Bmi(self) -> float:
        return self.Weight / (self.Height ** 2)


class Userinput(BaseModel):
    symptom: List[str]


class FoodItems(BaseModel):
    food_list: list[str]


# === Routes ===
@fastapi_app.get("/", tags=["Root"])
def root():
    return {"status": "✅ FastAPI is running on Render"}


@fastapi_app.post("/predict_heart_attack_risk", tags=["Heart Attack Prediction"])
def predict_heart_attack(data: HeartAttackInput):
    if heart_model is None:
        return JSONResponse(status_code=503, content={"error": "Model still loading..."})
    df = pd.DataFrame([data.model_dump(by_alias=True)])
    prediction = heart_model.predict(df)[0]
    probability = heart_model.predict_proba(df)[0][1]
    return {"heart_attack_risk": bool(prediction), "risk_probability": round(probability, 4)}


@fastapi_app.post("/predict_calories", tags=["Calorie Prediction"])
def predict_calories(data: Caloriesinput):
    if calorie_model is None:
        return JSONResponse(status_code=503, content={"error": "Model still loading..."})
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
    return {'predicted_calories': float(prediction)}


@fastapi_app.post("/predict_dieases", tags=["Disease Prediction"])
def predict_diseases(data: Userinput):
    if disease_model is None or le is None:
        return JSONResponse(status_code=503, content={"error": "Model still loading..."})
    selected_symptoms = [s.strip().lower().replace(" ", "_") for s in data.symptom]
    input_vector = [1 if s in selected_symptoms else 0 for s in all_symptom]
    input_df = pd.DataFrame([input_vector], columns=all_symptom)
    probs = disease_model.predict_proba(input_df)[0]
    top_indices = probs.argsort()[-3:][::-1]
    top_diseases = le.inverse_transform(top_indices)
    top_probs = [round(probs[i] * 100, 2) for i in top_indices]
    result = [{"disease": d, "confidence": p} for d, p in zip(top_diseases, top_probs)]
    return {"top_predictions": result}


@fastapi_app.post("/predict_daily_calories", tags=["Daily Intake Prediction"])
def predict_daily_calories(items: FoodItems):
    global intake_model
    if intake_model is None:
        load_intake_model()  # Lazy load here if not loaded yet
        if intake_model is None:
            return JSONResponse(status_code=503, content={"error": "intake.pkl still loading..."})
    results = []
    total = 0.0
    for food in items.food_list:
        food_cleaned = food.strip().lower()
        try:
            prediction = intake_model.predict([food_cleaned])[0]
            cal = round(float(prediction), 2)
            results.append({"food_item": food, "calories": cal})
            total += cal
        except Exception:
            results.append({"food_item": food, "calories": "unknown"})
    return {"total_calories": round(total, 2), "breakdown": results}
