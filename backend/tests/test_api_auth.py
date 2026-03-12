"""Unit tests for API authentication and authorization."""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4
import jwt

from app.api.auth import (
    create_access_token,
    verify_token,
    TokenData
)
from app.core.config import settings
from fastapi import HTTPException


class TestTokenCreation:
    """Tests for token creation."""

    def test_create_access_token_success(self):
        """Test successful token creation."""
        user_id = uuid4()
        role = "credit_officer"
        
        token = create_access_token(user_id, role)
        
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_expiry(self):
        """Test token creation with custom expiry."""
        user_id = uuid4()
        role = "credit_officer"
        expires_delta = timedelta(hours=1)
        
        token = create_access_token(user_id, role, expires_delta)
        
        assert isinstance(token, str)

    def test_token_contains_user_id(self):
        """Test that token contains user ID."""
        user_id = uuid4()
        role = "credit_officer"
        
        token = create_access_token(user_id, role)
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        assert payload["user_id"] == str(user_id)

    def test_token_contains_role(self):
        """Test that token contains role."""
        user_id = uuid4()
        role = "credit_officer"
        
        token = create_access_token(user_id, role)
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        assert payload["role"] == role

    def test_token_contains_expiry(self):
        """Test that token contains expiry time."""
        user_id = uuid4()
        role = "credit_officer"
        
        token = create_access_token(user_id, role)
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        assert "exp" in payload
        assert payload["exp"] > datetime.utcnow().timestamp()


class TestTokenVerification:
    """Tests for token verification."""

    def test_verify_token_success(self):
        """Test successful token verification."""
        user_id = uuid4()
        role = "credit_officer"
        token = create_access_token(user_id, role)
        
        token_data = verify_token(token)
        
        assert isinstance(token_data, TokenData)
        assert token_data.user_id == user_id
        assert token_data.role == role

    def test_verify_invalid_token(self):
        """Test verification of invalid token."""
        with pytest.raises(HTTPException) as exc_info:
            verify_token("invalid_token")
        
        assert exc_info.value.status_code == 401

    def test_verify_expired_token(self):
        """Test verification of expired token."""
        user_id = uuid4()
        role = "credit_officer"
        
        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)
        token = create_access_token(user_id, role, expires_delta)
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)
        
        assert exc_info.value.status_code == 401
        assert "expired" in exc_info.value.detail.lower()

    def test_verify_token_missing_user_id(self):
        """Test verification of token missing user_id."""
        payload = {
            "role": "credit_officer",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)
        
        assert exc_info.value.status_code == 401

    def test_verify_token_missing_role(self):
        """Test verification of token missing role."""
        payload = {
            "user_id": str(uuid4()),
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)
        
        assert exc_info.value.status_code == 401


class TestTokenData:
    """Tests for TokenData class."""

    def test_token_data_creation(self):
        """Test TokenData creation."""
        user_id = uuid4()
        role = "credit_officer"
        exp = datetime.utcnow() + timedelta(hours=1)
        
        token_data = TokenData(user_id, role, exp)
        
        assert token_data.user_id == user_id
        assert token_data.role == role
        assert token_data.exp == exp

    def test_token_data_different_roles(self):
        """Test TokenData with different roles."""
        user_id = uuid4()
        
        for role in ["credit_officer", "viewer", "admin"]:
            token_data = TokenData(user_id, role, datetime.utcnow())
            assert token_data.role == role


class TestTokenRoundTrip:
    """Tests for token creation and verification round trip."""

    def test_create_and_verify_token(self):
        """Test creating and verifying a token."""
        user_id = uuid4()
        role = "credit_officer"
        
        token = create_access_token(user_id, role)
        token_data = verify_token(token)
        
        assert token_data.user_id == user_id
        assert token_data.role == role

    def test_multiple_tokens_different_users(self):
        """Test creating tokens for different users."""
        user_id_1 = uuid4()
        user_id_2 = uuid4()
        role = "credit_officer"
        
        token_1 = create_access_token(user_id_1, role)
        token_2 = create_access_token(user_id_2, role)
        
        token_data_1 = verify_token(token_1)
        token_data_2 = verify_token(token_2)
        
        assert token_data_1.user_id == user_id_1
        assert token_data_2.user_id == user_id_2
        assert token_data_1.user_id != token_data_2.user_id

    def test_multiple_tokens_different_roles(self):
        """Test creating tokens with different roles."""
        user_id = uuid4()
        
        token_officer = create_access_token(user_id, "credit_officer")
        token_viewer = create_access_token(user_id, "viewer")
        
        token_data_officer = verify_token(token_officer)
        token_data_viewer = verify_token(token_viewer)
        
        assert token_data_officer.role == "credit_officer"
        assert token_data_viewer.role == "viewer"
