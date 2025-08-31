from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime,Text, Boolean,Date,Time,func,JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from . import Base
from werkzeug.security import generate_password_hash, check_password_hash


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    hash_password = Column(String)
    name = Column(String)
    email = Column(String, unique=True)
    age = Column(Integer)
    gender = Column(String)
    weight = Column(Float)
    height = Column(Float)
    blood_group = Column(String)
    contact = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    google_token = Column(String)

    health_records = relationship("HealthRecord", back_populates="user", cascade="all, delete")
    prescriptions = relationship("Prescription", back_populates="user", cascade="all, delete")
    alerts = relationship("Alert", back_populates="user")
    profile = relationship("Profile", back_populates="user")
    user_goals = relationship("UserGoal", back_populates="user")
    intake = relationship("Intake", back_populates="user") 
    medications = relationship("Medication", back_populates="user", cascade="all, delete-orphan") 


    def set_password(self, password):
        self.hash_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hash_password, password)


class HealthRecord(Base):
    __tablename__ = 'health_records'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    heart_rate = Column(Integer)
    blood_pressure = Column(String)
    oxygen_saturation = Column(Integer)
    stress_level = Column(String)
    sleep_hours = Column(Float)
    calories_burned = Column(Integer)
    steps = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="health_records")


class Prescription(Base):
    __tablename__ = 'prescriptions'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))  # Adjust if your users table name is different
    prescription_name = Column(String(255), nullable=False)
    image_url = Column(String(512))
    ocr_text = Column(Text)  # <-- ADD THIS LINE if not present
    predicted_disease = Column(String(100))
    medicines_json = Column(JSON)
    uploaded_at = Column(DateTime)

    user = relationship("User", back_populates="prescriptions")


class UserGoal(Base):
    __tablename__ = 'user_goals'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    goal_type = Column(String(50), nullable=False)
    target_value = Column(Float, nullable=False)
    unit = Column(String(20), nullable=False)
    frequency = Column(String(20), default='daily')
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    current_progress = Column(Float, default=0.0)
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="user_goals")
    daily_progress = relationship("DailyGoalProgress", back_populates="goal", cascade="all, delete-orphan")    

    def __repr__(self):
        return f'<Goal {self.goal_type} - User {self.user_id}>'


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="alerts")


class Profile(Base):
    __tablename__ = "profile"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    age = Column(Float)
    cholesterol = Column(Float)
    heart_rate = Column(Float)
    diabetes = Column(Boolean)
    family_history = Column(Boolean)
    smoking = Column(Boolean)
    obesity = Column(Boolean)
    alcohol_consumption = Column(Boolean)
    exercise_hours_per_day = Column(Float)
    diet = Column(Integer)
    previous_heart_problems = Column(Boolean)
    medication_use = Column(Boolean)
    stress_level = Column(String)
    sedentary_hours_per_day = Column(Float)
    bmi = Column(Float)
    sleep_hours_per_day = Column(Float)
    heart_attack_risk_binary = Column(Boolean)
    blood_sugar = Column(Float)
    systolic_blood_pressure = Column(Float)
    diastolic_blood_pressure = Column(Float)
    photo = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    diet_type = Column(String)  # e.g., "keto", "low_carb", "high_protein"
    allergies = Column(String)  # or a comma-separated string

    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<HeartAttackRiskRecord(id={self.id}, risk={self.heart_attack_risk_binary})>"

class Intake(Base):
    __tablename__="intake"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    calorie_intake=Column(Integer)
    water_intake=Column(Float)
    meal_time = Column(DateTime)
    
    updates_at= Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="intake")


from datetime import datetime, date


def today_date():
    return date.today()



class DailyGoalProgress(Base):
    __tablename__ = 'daily_goal_progress'

    id = Column(Integer, primary_key=True)
    user_goal_id = Column(Integer, ForeignKey('user_goals.id'))
    date = Column(Date, default=today_date)  # ✅ CORRECT
    progress = Column(Integer, default=0)

    goal = relationship("UserGoal", back_populates="daily_progress")
class Medication(Base):
    __tablename__ = "medications"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    dosage = Column(String)
    time = Column(Time)  # Reminder time
    start_date = Column(Date)
    end_date = Column(Date)
    taken_today = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="medications")

