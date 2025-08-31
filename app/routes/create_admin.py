from app.model import User
from sqlalchemy.exc import IntegrityError
from app import sessionLocal

def create_admin():
    db = sessionLocal()
    admin = User(
        username='admin',
        name='Admin User',
        email='admin@example.com',
        age=30,
        gender='Male',
        weight=70,
        height=170,
        blood_group='O+',
        contact='1234567890',
        is_admin=True
    )
    admin.set_password('admin123')  
    try:
        db.add(admin)
        db.commit()
        print("✅ Admin user created successfully.")
    except IntegrityError:
        db.rollback()
        print("⚠️ Admin user already exists.")
    finally:
        db.close()        