import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score
import pickle  # for saving model

# Step 1: Load dataset
df = pd.read_csv("C:\\Users\\Lenovo\\OneDrive\\ドキュメント\\heart-attack-risk-prediction-dataset.csv")
  
df=df.drop(columns=['Income','Triglycerides','Physical Activity Days Per Week','Heart Attack Risk (Text)','CK-MB', 'Troponin'])
print(df.columns)
X = df.drop(columns=["Heart Attack Risk (Binary)"])
y = df["Heart Attack Risk (Binary)"].astype(int)

# Step 4: Identify feature types
numeric_cols = X.select_dtypes(include=["float64", "int64"]).columns.tolist()
categorical_cols = ["Gender", "Diet"] if "Gender" in X.columns else ["Diet"]

# Step 5: Preprocessing pipelines
numeric_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median"))
])

categorical_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore"))
])

preprocessor = ColumnTransformer([
    ("num", numeric_pipeline, numeric_cols),
    ("cat", categorical_pipeline, categorical_cols)
])

# Step 6: Complete pipeline with classifier
model = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", RandomForestClassifier(n_estimators=100, random_state=42))
])

# Step 7: Train/Test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Step 8: Fit model
model.fit(X_train, y_train)

# Step 9: Evaluate model
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

print("✅ Accuracy:", accuracy_score(y_test, y_pred))
print("✅ ROC AUC:", roc_auc_score(y_test, y_prob))
print("✅ Classification Report:\n", classification_report(y_test, y_pred))

# Step 10: Save model
with open("pickle_files/heart_attack_risk_model.pkl",'wb') as f:
   
   pickle.dump(model,f)
print("✅ Model saved as 'heart_attack_risk_model.pkl'")
import sklearn 
print(sklearn.__version__)