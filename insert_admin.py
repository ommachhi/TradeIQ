from database.db import SessionLocal
from database.models import User
from auth.auth import hash_password

def seed_admin():
    db = SessionLocal()
    existing = db.query(User).filter(User.email == "admin@tredalq.com").first()
    if not existing:
        admin = User(
            name="Super Admin",
            email="admin@tredalq.com",
            password_hash=hash_password("Admin@123!"),
            role="Admin",
            is_active=True
        )
        db.add(admin)
        db.commit()
        print("Admin user created (admin@tredalq.com / Admin@123!)")
    else:
        print("Admin user already exists.")
    db.close()

if __name__ == "__main__":
    seed_admin()
