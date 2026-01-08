"""
Authentication Module for VITA-Care
Handles user registration, login, JWT tokens, and password hashing
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import bcrypt  # Direct bcrypt instead of passlib
from jose import JWTError, jwt
from dotenv import load_dotenv

load_dotenv()

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "vita-care-super-secret-key-change-in-production-min-32-chars")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt (direct implementation)
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password as string
    """
    # Convert password to bytes and hash
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    # Return as string for database storage
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password from database
    
    Returns:
        True if password matches, False otherwise
    """
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Payload data (typically contains user_id, username)
        expires_delta: Optional custom expiration time
    
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode and validate a JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError as e:
        print(f"JWT Decode Error: {e}")
        return None


def extract_user_from_token(token: str) -> Optional[str]:
    """
    Extract user ID from JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        User ID (pid) if valid, None otherwise
    """
    payload = decode_access_token(token)
    if payload:
        return payload.get("sub")  # 'sub' is standard JWT claim for subject (user_id)
    return None


# Test functions
if __name__ == "__main__":
    # Test password hashing
    test_password = "SecurePassword123!"
    hashed = hash_password(test_password)
    print(f"Original: {test_password}")
    print(f"Hashed: {hashed}")
    print(f"Verification: {verify_password(test_password, hashed)}")
    
    # Test JWT creation
    test_data = {"sub": "user123", "username": "testuser"}
    token = create_access_token(test_data)
    print(f"\nJWT Token: {token}")
    
    decoded = decode_access_token(token)
    print(f"Decoded: {decoded}")
