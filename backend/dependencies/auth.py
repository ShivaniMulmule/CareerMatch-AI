"""
Authentication and JWT Security Dependencies for CareerMatch AI.
Implements direct bcrypt password hashing and JWT bearer token authorization.
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import bcrypt

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from database.db_client import get_database


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "careermatch-ai-super-secure-production-key-2026-btech")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

security_bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """Hash plaintext password with bcrypt (truncated to 72 bytes per bcrypt spec)."""
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plaintext password against bcrypt hash."""
    try:
        pwd_bytes = plain_password.encode("utf-8")[:72]
        hash_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        return False


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Generate signed JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: Any = Depends(get_database)
) -> Dict[str, Any]:
    """
    FastAPI dependency: verifies Bearer token, loads user record,
    and returns authenticated user dictionary.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token expired",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not credentials:
        raise credentials_exception

    token = credentials.credentials
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    users_col = db.get_collection("users") if hasattr(db, "get_collection") else db["users"]
    user = await users_col.find_one({"_id": user_id})
    if user is None:
        raise credentials_exception

    return user
