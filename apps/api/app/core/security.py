"""
Security utilities for authentication and authorization
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Payload data to encode in token
        expires_delta: Optional custom expiration time
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access",
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT refresh token
    
    Args:
        data: Payload data to encode in token
        expires_delta: Optional custom expiration time
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh",
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.algorithm
    )
    
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload or None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError as e:
        logger.warning(f"Token decode failed: {e}")
        return None


def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify access token and return payload
    
    Args:
        token: JWT access token
    
    Returns:
        Token payload if valid, None otherwise
    """
    payload = decode_token(token)
    
    if payload is None:
        return None
    
    if payload.get("type") != "access":
        logger.warning("Token is not an access token")
        return None
    
    return payload


def verify_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify refresh token and return payload
    
    Args:
        token: JWT refresh token
    
    Returns:
        Token payload if valid, None otherwise
    """
    payload = decode_token(token)
    
    if payload is None:
        return None
    
    if payload.get("type") != "refresh":
        logger.warning("Token is not a refresh token")
        return None
    
    return payload


def create_password_reset_token(email: str) -> str:
    """
    Create password reset token
    
    Args:
        email: User email address
    
    Returns:
        Password reset token
    """
    data = {"sub": email, "type": "reset"}
    expire = datetime.utcnow() + timedelta(hours=1)
    data.update({"exp": expire, "iat": datetime.utcnow()})
    
    return jwt.encode(data, settings.secret_key, algorithm=settings.algorithm)


def verify_password_reset_token(token: str) -> Optional[str]:
    """
    Verify password reset token and return email
    
    Args:
        token: Password reset token
    
    Returns:
        Email if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        
        if payload.get("type") != "reset":
            return None
        
        email = payload.get("sub")
        return email if email else None
        
    except JWTError:
        return None