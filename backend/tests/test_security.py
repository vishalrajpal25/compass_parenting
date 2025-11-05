"""
Tests for security utilities (password hashing, JWT tokens).
"""
import pytest
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)


def test_password_hashing():
    """Test password hashing and verification."""
    password = "testpassword123"
    hashed = get_password_hash(password)

    # Verify correct password
    assert verify_password(password, hashed)

    # Verify incorrect password
    assert not verify_password("wrongpassword", hashed)


def test_create_access_token():
    """Test JWT access token creation."""
    user_id = 123
    token = create_access_token(subject=user_id)

    # Decode and verify
    payload = decode_token(token)
    assert payload["sub"] == str(user_id)
    assert payload["type"] == "access"


def test_create_refresh_token():
    """Test JWT refresh token creation."""
    user_id = 456
    token = create_refresh_token(subject=user_id)

    # Decode and verify
    payload = decode_token(token)
    assert payload["sub"] == str(user_id)
    assert payload["type"] == "refresh"


def test_token_with_additional_claims():
    """Test token creation with additional claims."""
    user_id = 789
    additional_claims = {"email": "test@example.com", "role": "admin"}
    token = create_access_token(subject=user_id, additional_claims=additional_claims)

    # Decode and verify
    payload = decode_token(token)
    assert payload["sub"] == str(user_id)
    assert payload["email"] == "test@example.com"
    assert payload["role"] == "admin"
