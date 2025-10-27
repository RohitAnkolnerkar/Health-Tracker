from flask import Flask,Blueprint,render_template,flash,jsonify,redirect,url_for,request,make_response
from app.model import User,HealthRecord
from datetime import datetime
from app import sessionLocal
import csv
from io import StringIO
admin_bp=Blueprint('admin',__name__,url_prefix='/admin')
@admin_bp.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    db = sessionLocal()
    all_users = db.query(User).all()
    total_users = db.query(User).count()
    all_records = []
    if request.method == 'POST':
        user_id = request.form.get("user_id")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        download = request.form.get("download")

        fields = request.form.getlist("filter_field")
        conditions = request.form.getlist("filter_condition")
        values = request.form.getlist("filter_value")

        query = db.query(HealthRecord)

        if user_id != 'all':
            query = query.filter(HealthRecord.user_id == int(user_id))

        try:
            if start_date:
                query = query.filter(HealthRecord.created_at >= datetime.strptime(start_date, "%Y-%m-%d"))
            if end_date:
                query = query.filter(HealthRecord.created_at <= datetime.strptime(end_date, "%Y-%m-%d"))
        except ValueError:
            pass

        from sqlalchemy import and_

        filter_conditions = []

        for field, cond, val in zip(fields, conditions, values):
            if field and cond and val:
                column = getattr(HealthRecord, field, None)
                if column is not None:
                    try:
                        val = float(val)
                        if cond == '>':
                            filter_conditions.append(column > val)
                        elif cond == '<':
                            filter_conditions.append(column < val)
                        elif cond == '=':
                            filter_conditions.append(column == val)
                    except ValueError:
                        continue

        if filter_conditions:
            query = query.filter(and_(*filter_conditions))

        all_records = query.all()

        # ✅ If download is requested
        if download == 'yes':
            # Create CSV
            si = StringIO()
            writer = csv.writer(si)

            # Header
            writer.writerow([
                "User ID", "Heart Rate", "Blood Pressure", "Oxygen Saturation", 
                "Stress Level", "Sleep Hours", "Calories Burned", "Recorded At"
            ])

            # Rows
            for record in all_records:
                writer.writerow([
                    record.user_id,
                    record.heart_rate,
                    record.blood_pressure,
                    record.oxygen_saturation,
                    record.stress_level,
                    record.sleep_hours,
                    record.calories_burned,
                    record.created_at.strftime("%Y-%m-%d %H:%M:%S")
                ])

            output = make_response(si.getvalue())
            output.headers["Content-Disposition"] = "attachment; filename=filtered_health_records.csv"
            output.headers["Content-type"] = "text/csv"
            db.close()
            return output

    db.close()
    return render_template(
        'Admin_dashboard.html',
        total_users=total_users,
        users=all_users,
        records=all_records
    )

     

@admin_bp.route('/admin/delete_user/<int:user_id>',methods=['POST']) 
def delete_user(user_id):
    db=sessionLocal
    try:
        user=db.query(User).get(user_id)
        if not user:
            return jsonify({'message':"invalid User"}),404 
        user.is_active=False
        db.commit()
        flash("user status updates")
        return redirect(url_for("admin.admin_dashboard"))
    finally:
        db.close()
       

     

    

