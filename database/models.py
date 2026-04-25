from sqlalchemy import create_all, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    role = Column(String(20), default='user') # 'user' or 'admin'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="user")
    watchlist = relationship("Watchlist", back_populates="user")
    history = relationship("PredictionHistory", back_populates="user")

class Portfolio(Base):
    __tablename__ = 'portfolio'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    symbol = Column(String(20), nullable=False)
    quantity = Column(Integer, default=0)
    buy_price = Column(Float, default=0.0)
    added_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="portfolio")

class Watchlist(Base):
    __tablename__ = 'watchlist'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    symbol = Column(String(20), nullable=False)
    
    user = relationship("User", back_populates="watchlist")

class PredictionHistory(Base):
    __tablename__ = 'prediction_history'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    symbol = Column(String(20), nullable=False)
    current_price = Column(Float)
    predicted_price = Column(Float)
    signal = Column(String(10)) # BUY, SELL, HOLD
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="history")
