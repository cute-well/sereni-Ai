"""Database models for Sereni."""

from __future__ import annotations

from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import relationship

from database import db

MessageRole = Enum("user", "assistant", "system", name="message_role")
RiskLevel = Enum("low", "moderate", "high", name="risk_level")


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(120), nullable=False)
    is_active = Column(db.Boolean, default=True, nullable=False)
    is_admin = Column(db.Boolean, default=False, nullable=False)
    failed_logins = Column(Integer, default=0, nullable=False)
    last_login_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    messages = relationship("Message", back_populates="user", cascade="all, delete-orphan")
    risk_events = relationship(
        "RiskEvent", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - repr helper
        return f"<User {self.email}>"


class Message(db.Model):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role = Column(MessageRole, nullable=False)
    content = Column(Text, nullable=False)
    sentiment = Column(String(32), nullable=True)
    sentiment_score = Column(Numeric(5, 4), nullable=True)
    risk_score = Column(Numeric(5, 4), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="messages")
    risk_event = relationship(
        "RiskEvent", back_populates="message", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - repr helper
        return f"<Message {self.id} role={self.role}>"


class RiskEvent(db.Model):
    __tablename__ = "risk_events"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="SET NULL"))
    level = Column(RiskLevel, nullable=False)
    risk_score = Column(Numeric(5, 4), nullable=False)
    trigger = Column(String(120), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="risk_events")
    message = relationship("Message", back_populates="risk_event")

    def __repr__(self) -> str:  # pragma: no cover - repr helper
        return f"<RiskEvent {self.id} level={self.level}>"
