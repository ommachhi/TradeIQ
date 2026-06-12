import bcrypt
import streamlit as st
from datetime import datetime
from database.mongo_client import get_db

def register_user(name: str, email: str, password: str) -> dict:
    db = get_db()
    if db.users.find_one({"email": email}):
        return {"success": False, "error": "Email already registered"}
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    user = {
        "name": name,
        "email": email,
        "password": hashed,
        "role": "user",
        "created_at": datetime.utcnow(),
        "watchlist": [],
        "portfolio": []
    }
    result = db.users.insert_one(user)
    return {"success": True, "user_id": str(result.inserted_id)}

def login_user(email: str, password: str) -> dict:
    db = get_db()
    user = db.users.find_one({"email": email})
    if not user:
        return {"success": False, "error": "User not found"}
    if not bcrypt.checkpw(password.encode(), user["password"]):
        return {"success": False, "error": "Invalid password"}
    st.session_state["user"] = {
        "_id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "role": user["role"]
    }
    return {"success": True}

def logout_user():
    st.session_state.pop("user", None)
    st.rerun()

def get_current_user():
    return st.session_state.get("user", None)

def require_auth():
    if not get_current_user():
        st.switch_page("pages/login.py")
