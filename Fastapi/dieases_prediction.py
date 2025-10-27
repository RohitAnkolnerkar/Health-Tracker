import pandas as pd
import pickle
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
from sklearn.calibration import CalibratedClassifierCV

# Load data
data = pd.read_csv("Datasets\Training.csv")
test = pd.read_csv("Datasets\Testing.csv")
df = data.drop(columns=['Unnamed: 133'])

# Encode labels
le = LabelEncoder()
Y_train = le.fit_transform(df['prognosis'])
X_train = df.drop(columns=['prognosis'])

Y_test = le.transform(test['prognosis'])
X_test = test.drop(columns=['prognosis'])

# Feature list
columns_list = X_train.columns.to_list()

# Base classifier
rf = RandomForestClassifier(n_estimators=100, random_state=42)

# Wrap in CalibratedClassifierCV
calibrated_rf = CalibratedClassifierCV(estimator=rf, method='sigmoid', cv=5)

# Pipeline with calibrated classifier
pipeline = Pipeline([
    ('classifier', calibrated_rf)
])

# Train
pipeline.fit(X_train, Y_train)

# Predict
y_pred = pipeline.predict(X_test)
print("Accuracy:", accuracy_score(Y_test, y_pred))
print("Classification Report:\n", classification_report(Y_test, y_pred, target_names=le.classes_))

# Save model
with open("pickle_files/Dieases.pkl", 'wb') as f:
    pickle.dump((pipeline, le, columns_list), f)
