import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score
import pickle  # for saving model
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
df = pd.read_csv("Datasets\recipes.csv")
df.columns
df=df[['Name','Calories']]
df['Name'] = df['Name'].str.lower().str.strip()
df=df.iloc[:50000,:]
X_train, X_test, y_train, y_test = train_test_split(df['Name'], df['Calories'], test_size=0.2, random_state=42)
model = Pipeline([
    ('vectorizer', TfidfVectorizer(ngram_range=(1, 2), max_features=10000)),
    ('regressor', RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1))
])
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
print("MAE:", mean_absolute_error(y_test, y_pred))
print("R² Score:", r2_score(y_test, y_pred))
with open("C:\\Users\\Lenovo\\OneDrive\\Desktop\\Ai health Traker\\pickle_files\\intake.pkl",'wb') as f:
    pickle.dump(model,f)
 