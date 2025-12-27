"""Tests for Authentication Service"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import using helper to handle hyphenated directory names
from tests.import_helpers import import_service_module

try:
    auth_module = import_service_module("auth-service", "main")
    app = auth_module.app
    create_access_token = auth_module.create_access_token
    verify_password = auth_module.verify_password
    get_password_hash = auth_module.get_password_hash
    from jose import jwt
except (ImportError, AttributeError) as e:
    pytest.skip(f"Could not import auth service: {e}", allow_module_level=True)


class TestAuthServiceAPI:
    """Test Authentication Service API endpoints"""
    
    @pytest.fixture
    def client(self):
        """Create test client"""
        return TestClient(app)
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "auth-service"
    
    @patch('services.auth_service.main.get_db_client')
    def test_register_success(self, mock_db, client):
        """Test successful user registration"""
        mock_db_instance = MagicMock()
        mock_db_instance.execute_query.return_value = []  # No existing user
        mock_db_instance.execute_update.return_value = True
        mock_db.return_value = mock_db_instance
        
        response = client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"
    
    @patch('services.auth_service.main.get_db_client')
    def test_register_duplicate(self, mock_db, client):
        """Test registration with duplicate username"""
        mock_db_instance = MagicMock()
        mock_db_instance.execute_query.return_value = [{"username": "testuser"}]  # Existing user
        mock_db.return_value = mock_db_instance
        
        response = client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    @patch('services.auth_service.main.get_db_client')
    def test_login_success(self, mock_db, client):
        """Test successful login"""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        hashed = pwd_context.hash("testpassword123")
        
        mock_db_instance = MagicMock()
        mock_db_instance.execute_query.return_value = [{
            "username": "testuser",
            "hashed_password": hashed
        }]
        mock_db.return_value = mock_db_instance
        
        response = client.post(
            "/login",
            json={
                "username": "testuser",
                "password": "testpassword123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    @patch('services.auth_service.main.get_db_client')
    def test_login_invalid_credentials(self, mock_db, client):
        """Test login with invalid credentials"""
        mock_db_instance = MagicMock()
        mock_db_instance.execute_query.return_value = []  # User not found
        mock_db.return_value = mock_db_instance
        
        response = client.post(
            "/login",
            json={
                "username": "testuser",
                "password": "wrongpassword"
            }
        )
        
        assert response.status_code == 401
    
    @patch('services.auth_service.main.get_db_client')
    def test_get_current_user(self, mock_db, client):
        """Test getting current user info"""
        import os
        os.environ["JWT_SECRET_KEY"] = "test-secret-key"
        
        # Create valid token
        token = create_access_token({"sub": "testuser"})
        
        mock_db_instance = MagicMock()
        mock_db_instance.execute_query.return_value = [{
            "username": "testuser",
            "email": "test@example.com"
        }]
        mock_db.return_value = mock_db_instance
        
        response = client.get(
            "/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
    
    def test_verify_token_endpoint(self, client):
        """Test token verification endpoint"""
        import os
        os.environ["JWT_SECRET_KEY"] = "test-secret-key"
        
        token = create_access_token({"sub": "testuser"})
        
        response = client.get(
            "/verify",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True


class TestAuthUtilities:
    """Test authentication utilities"""
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrongpassword", hashed) is False
    
    def test_create_access_token(self):
        """Test JWT token creation"""
        import os
        os.environ["JWT_SECRET_KEY"] = "test-secret-key"
        
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        
        # Verify token can be decoded
        decoded = jwt.decode(token, "test-secret-key", algorithms=["HS256"])
        assert decoded["sub"] == "testuser"

