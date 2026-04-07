"""Password hashing utilities using bcrypt."""

from __future__ import annotations

from typing import Union

import bcrypt

Hashable = Union[str, bytes]


def _ensure_bytes(value: Hashable) -> bytes:
    return value.encode("utf-8") if isinstance(value, str) else value


def generate_hash(password: Hashable) -> str:
    """Return a bcrypt hash for the given password."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(_ensure_bytes(password), salt)
    return hashed.decode("utf-8")


def verify_password(password: Hashable, hashed: Hashable) -> bool:
    """Verify a password against a stored hash."""
    try:
        return bcrypt.checkpw(_ensure_bytes(password), _ensure_bytes(hashed))
    except ValueError:
        return False
