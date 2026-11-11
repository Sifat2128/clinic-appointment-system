"""Tests for Authentication, Password Security, Repository, and RBAC."""
import pytest
from backend.app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from backend.app.models.user import User, UserRole
from backend.app.repositories.user_repository import UserRepository


def test_password_hashing_and_verification():
    raw_password = "SecurePassword@123"
    hashed = get_password_hash(raw_password)
    assert hashed != raw_password
    assert verify_password(raw_password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token_creation_and_decoding():
    payload_data = {"sub": "admin@clinic.com", "role": "admin", "user_id": 1}
    token = create_access_token(payload_data)
    assert isinstance(token, str)
    
    decoded = decode_access_token(token)
    assert decoded["sub"] == "admin@clinic.com"
    assert decoded["role"] == "admin"
    assert decoded["user_id"] == 1


def test_user_repository_crud(db_session):
    repo = UserRepository(db_session)
    user = User(
        email="doctor.tanvir@clinic.com",
        full_name="Dr. Tanvir Rahman",
        hashed_password=get_password_hash("DocPass123!"),
        role=UserRole.DOCTOR.value,
        is_active=True,
    )
    created_user = repo.create(user)
    assert created_user.id is not None
    assert created_user.email == "doctor.tanvir@clinic.com"

    # Get by email
    found_by_email = repo.get_by_email("doctor.tanvir@clinic.com")
    assert found_by_email is not None
    assert found_by_email.id == created_user.id

    # Get by id
    found_by_id = repo.get_by_id(created_user.id)
    assert found_by_id is not None
    assert found_by_id.full_name == "Dr. Tanvir Rahman"

    # Get all
    all_users = repo.get_all()
    assert len(all_users) >= 1


def test_login_success(client, db_session):
    repo = UserRepository(db_session)
    user = User(
        email="receptionist@clinic.com",
        full_name="Sarah Receptionist",
        hashed_password=get_password_hash("ReceptPass123!"),
        role=UserRole.RECEPTIONIST.value,
        is_active=True,
    )
    repo.create(user)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "receptionist@clinic.com", "password": "ReceptPass123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "receptionist@clinic.com"
    assert data["user"]["role"] == "receptionist"


def test_login_invalid_credentials(client, db_session):
    repo = UserRepository(db_session)
    user = User(
        email="admin@clinic.com",
        full_name="Admin User",
        hashed_password=get_password_hash("AdminPass123!"),
        role=UserRole.ADMIN.value,
        is_active=True,
    )
    repo.create(user)

    # Wrong password
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@clinic.com", "password": "IncorrectPassword"},
    )
    assert response.status_code == 401
    assert "Invalid email or password" in response.json()["detail"]

    # Non-existent user
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "ghost@clinic.com", "password": "AnyPassword"},
    )
    assert response.status_code == 401


def test_get_current_user_me(client, db_session):
    repo = UserRepository(db_session)
    user = User(
        email="admin@clinic.com",
        full_name="Admin User",
        hashed_password=get_password_hash("AdminPass123!"),
        role=UserRole.ADMIN.value,
        is_active=True,
    )
    created = repo.create(user)

    token = create_access_token({"sub": created.email, "role": created.role, "user_id": created.id})
    response = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "admin@clinic.com"
    assert data["role"] == "admin"


def test_admin_can_create_staff_users(client, db_session):
    repo = UserRepository(db_session)
    admin = User(
        email="superadmin@clinic.com",
        full_name="Super Admin",
        hashed_password=get_password_hash("SuperAdmin123!"),
        role=UserRole.ADMIN.value,
        is_active=True,
    )
    created_admin = repo.create(admin)
    admin_token = create_access_token({"sub": created_admin.email, "role": created_admin.role, "user_id": created_admin.id})

    new_doctor_payload = {
        "email": "dr.smith@clinic.com",
        "full_name": "Dr. John Smith",
        "password": "DoctorSecure123!",
        "role": "doctor",
    }
    response = client.post(
        "/api/v1/users",
        json=new_doctor_payload,
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "dr.smith@clinic.com"
    assert data["role"] == "doctor"
    assert "password" not in data


def test_non_admin_cannot_create_staff_users(client, db_session):
    repo = UserRepository(db_session)
    receptionist = User(
        email="rec@clinic.com",
        full_name="Staff Rec",
        hashed_password=get_password_hash("RecPass123!"),
        role=UserRole.RECEPTIONIST.value,
        is_active=True,
    )
    created_rec = repo.create(receptionist)
    token = create_access_token({"sub": created_rec.email, "role": created_rec.role, "user_id": created_rec.id})

    response = client.post(
        "/api/v1/users",
        json={"email": "hacker@clinic.com", "full_name": "Hacker", "password": "123", "role": "admin"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
