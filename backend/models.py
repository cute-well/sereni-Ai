"""Simple data models backed by MongoDB."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

from bson import ObjectId
from flask_login import UserMixin


def _obj_id(value: str | ObjectId) -> ObjectId:
    return value if isinstance(value, ObjectId) else ObjectId(value)


@dataclass
class User(UserMixin):
    id: ObjectId
    email: str
    password_hash: str
    full_name: str
    is_active: bool = True
    is_admin: bool = False

    def get_id(self) -> str:
        return str(self.id)

    @classmethod
    def from_doc(cls, doc: dict[str, Any]) -> "User":
        return cls(
            id=doc["_id"],
            email=doc["email"],
            password_hash=doc["password_hash"],
            full_name=doc.get("full_name", ""),
            is_active=doc.get("is_active", True),
            is_admin=doc.get("is_admin", False),
        )


# DAO helpers ---------------------------------------------------------------

def find_user_by_email(db, email: str) -> Optional[User]:
    doc = db.users.find_one({"email": email.lower()})
    return User.from_doc(doc) if doc else None


def find_user_by_id(db, user_id: str) -> Optional[User]:
    try:
        oid = _obj_id(user_id)
    except Exception:
        return None
    doc = db.users.find_one({"_id": oid})
    return User.from_doc(doc) if doc else None
