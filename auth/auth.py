import re
import bcrypt
from datetime import datetime
from database.db import SessionLocal
from database.models import User
from utils.security import generate_jwt, check_password_strength

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode('utf-8'), hashed.encode('utf-8'))

def register_user(name, email, password):
    if not name or not email or not password:
        return False, "All fields are required."
        
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if not re.match(email_regex, email):
        return False, "Invalid email format."
        
    strength = check_password_strength(password)
    if strength["score"] < 3:
        return False, " ".join(strength["feedback"])

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            return False, "Email already registered."
            
        new_user = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
            role="User",
            is_active=True
        )
        db.add(new_user)
        db.commit()
        return True, "Registration successful."
    except Exception as e:
        db.rollback()
        return False, f"Database error: {str(e)}"
    finally:
        db.close()

def login_user(email, password):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.password_hash):
            return None, "Invalid email or password."
        
        if not user.is_active:
            return None, "Account is disabled. Please contact support."

        user.last_login = datetime.utcnow()
        db.commit()

        token = generate_jwt(user.id, user.role)
        
        user_dict = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "token": token
        }
        return user_dict, "Login successful."
    except Exception as e:
        return None, f"Database error: {str(e)}"
    finally:
        db.close()
