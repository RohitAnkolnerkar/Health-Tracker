from app.model import HealthRecord,User
from flask import Flask,render_template,request,Blueprint,flash,url_for,session,redirect
from app import sessionLocal


heal = Blueprint("health_records",__name__)

@heal.route("/user_health",methods=['GET'])
def user_health():
    
    
    if "user" in session:
      username=session['user']
      db_session=sessionLocal()

      try:
           
         user=db_session.query(User).filter_by(username=username).first()
         print(db_session.query(HealthRecord).count())

         records=db_session.query(HealthRecord).filter_by(user_id=user.id).all()
   
         return render_template('health.html',records=records,name=user.username) 
      finally:
       
       db_session.close()


   



