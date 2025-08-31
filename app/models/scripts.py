from sklearn.preprocessing import LabelEncoder
import joblib
import os

disease_labels = [
    "Diabetes", "Heart Disease", "Asthma", "Tuberculosis",
    "Hypertension", "Arthritis", "Cancer", "COVID-19"
]

encoder = LabelEncoder()
encoder.fit(disease_labels)

os.makedirs("app/models", exist_ok=True)
joblib.dump(encoder, "app/models/label_encoder.pkl")
print("✅ Encoder saved at app/models/label_encoder.pkl")
