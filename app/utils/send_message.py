from datetime import datetime, date
from collections import defaultdict
import requests
from app import sessionLocal
from app.model import User, Medication

user_reminders = defaultdict(list)

def send_sms(phone_number, message):
    url = "https://www.fast2sms.com/dev/bulkV2"
    headers = {
        'authorization': 'YOUR_FAST2SMS_API_KEY',  # replace with your actual key
        'Content-Type': "application/json"
    }
    payload = {
        "route": "v3",
        "sender_id": "FSTSMS",
        "message": message,
        "language": "english",
        "flash": 0,
        "numbers": phone_number
    }

    response = requests.post(url, json=payload, headers=headers)
    print("SMS sent:", response.json())


def send_medication_reminders():
    db = sessionLocal()
    now = datetime.now()

    users = db.query(User).all()

    for user in users:
        if not user.contact:
            continue

        medications = db.query(Medication).filter_by(user_id=user.id).all()

        for med in medications:
            if med.start_date <= date.today() <= med.end_date:
                if med.time.hour == now.hour and med.time.minute == now.minute:
                    message = f"💊 Reminder: {med.name} - {med.dosage}"
                    send_sms(user.contact, message)

                    msg = f"💊 Reminder: {med.name} - {med.dosage} sent at {med.time.strftime('%I:%M %p')}"
                    user_reminders[user.id].append(msg)

    db.close()
