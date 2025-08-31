# upload_csv.py
from flask import Blueprint, request, flash, redirect, render_template,session
import pandas as pd
from datetime import datetime
from app.model import HealthRecord,User  # import your HealthRecord model
from app import sessionLocal  # your SQLAlchemy session instance

def read_csv():
        try:
            # Read CSV file using pandas
            df = pd.read_csv("app/apple_watch_final_health_data.csv")
            
            # Convert 'record_date' column to datetime objects
            df['created_at'] = pd.to_datetime(df['created_at'])
            
            db = sessionLocal()
            # Iterate through each row and add a HealthRecord instance to the session
            if 'user' in session:
                  
                  username=session['user']
                  user=db.query(User).filter_by(username=username).first()
                  for index, row in df.iterrows():
                   
                   record = HealthRecord(
                        user_id =int(user.id),
                        created_at = row['created_at'],
                        blood_pressure = (row['blood_pressure']),
                        heart_rate = int(row['heart_rate']),
                        stress_level = (row['stress_level']),
                        sleep_hours =float(row['sleep_hours']),
                        calories_burned=int(row['calories_burned']),
                        oxygen_saturation=int(row['oxygen_saturation']),
                        steps=int(row['steps']) 
                    )
                   
                   db.add(record)
                  db.commit()
                  db.close()
            
        except Exception as e:
            flash("An error occurred while processing the file: " + str(e))
        
            
    
    