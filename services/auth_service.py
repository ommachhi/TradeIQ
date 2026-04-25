import bcrypt
from database.models import User
from sqlalchemy.orm import Session

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password for storing."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify a stored password against one provided by user."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    @staticmethod
    def register_user(db: Session, username: str, email: str, password: str):
        """Register a new user in the database."""
        # Check if user already exists
        if db.query(User).filter(User.username == username).first():
            return False, "Username already taken"
        
        if db.query(User).filter(User.email == email).first():
            return False, "Email already registered"

        new_user = User(
            username=username,
            email=email,
            password_hash=AuthService.hash_password(password)
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return True, new_user

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str):
        """Authenticate a user and return user object if successful."""
        user = db.query(User).filter(User.username == username).first()
        if user and AuthService.verify_password(password, user.password_hash):
            return user
        return None
