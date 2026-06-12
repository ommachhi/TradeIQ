import jwt
import datetime
import os
import re

SECRET_KEY = os.getenv("JWT_SECRET", "super-secret-tredalq-key-change-in-prod")

def generate_jwt(user_id: int, role: str) -> str:
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2),
        "iat": datetime.datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def verify_jwt(token: str) -> dict:
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        return {"error": "Token has expired."}
    except jwt.InvalidTokenError:
        return {"error": "Invalid token."}

def check_password_strength(password: str) -> dict:
    score = 0
    feedback = []
    if len(password) >= 8:
        score += 1
    else:
        feedback.append("Password must be at least 8 characters long.")
    if re.search(r"[A-Z]", password):
        score += 1
    else:
        feedback.append("Include at least one uppercase letter.")
    if re.search(r"[a-z]", password):
        score += 1
    else:
        feedback.append("Include at least one lowercase letter.")
    if re.search(r"\d", password):
        score += 1
    else:
        feedback.append("Include at least one number.")
    if re.search(r"[@$!%*?&#]", password):
        score += 1
    else:
        feedback.append("Include at least one special character (@$!%*?&#).")
    
    strength = "Weak"
    if score >= 4:
        strength = "Strong"
    elif score >= 3:
        strength = "Medium"
        
    return {
        "score": score,
        "strength": strength,
        "feedback": feedback
    }

def sanitize_input(text: str) -> str:
    # Basic XSS prevention
    return text.replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#x27;")
