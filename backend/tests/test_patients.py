"""Tests for Patient CRUD, Demographic Updates, Search, and Repository."""
from datetime import date
import pytest
from backend.app.core.security import get_password_hash, create_access_token
from backend.app.models.user import User, UserRole
from backend.app.models.patient import Patient
from backend.app.repositories.patient_repository import PatientRepository


@pytest.fixture
def auth_headers(db_session):
    user = User(
        email="receptionist.patient@clinic.com",
        full_name="Staff Receptionist",
        hashed_password=get_password_hash("Staff123!"),
        role=UserRole.RECEPTIONIST.value,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token({"sub": user.email, "role": user.role, "user_id": user.id})
    return {"Authorization": f"Bearer {token}"}


def test_patient_repository_operations(db_session):
    repo = PatientRepository(db_session)
    patient = Patient(
        full_name="Mohammad Rahim",
        date_of_birth=date(1990, 5, 14),
        gender="Male",
        phone="+8801712345678",
        address="Dhaka, Bangladesh",
        emergency_contact="01812345678",
        medical_history="Hypertension",
        allergies="Penicillin",
    )
    created = repo.create(patient)
    assert created.id is not None
    assert created.full_name == "Mohammad Rahim"

    # Search by name substring
    search_results = repo.search("Rahim")
    assert len(search_results) == 1
    assert search_results[0].full_name == "Mohammad Rahim"

    # Search by phone substring
    phone_results = repo.search("017123")
    assert len(phone_results) == 1

    # Update patient
    updated = repo.update(created.id, {"allergies": "Penicillin, Sulfa drugs"})
    assert updated.allergies == "Penicillin, Sulfa drugs"

    # Delete patient
    assert repo.delete(created.id) is True
    assert repo.get_by_id(created.id) is None


def test_create_patient_api(client, auth_headers):
    payload = {
        "full_name": "Ayesha Siddiqua",
        "date_of_birth": "1995-10-20",
        "gender": "Female",
        "phone": "+8801911223344",
        "address": "Chittagong, Bangladesh",
        "emergency_contact": "01799887766",
        "medical_history": "Asthma",
        "allergies": "Dust, Pollen",
    }
    response = client.post("/api/v1/patients", json=payload, headers=auth_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert data["full_name"] == "Ayesha Siddiqua"
    assert data["phone"] == "+8801911223344"


def test_list_and_search_patients_api(client, auth_headers, db_session):
    repo = PatientRepository(db_session)
    repo.create(Patient(full_name="Alice Wonder", date_of_birth=date(1985, 1, 1), gender="Female", phone="01711111111"))
    repo.create(Patient(full_name="Bob Builder", date_of_birth=date(1980, 2, 2), gender="Male", phone="01822222222"))

    # List all
    res_all = client.get("/api/v1/patients", headers=auth_headers)
    assert res_all.status_code == 200
    assert len(res_all.json()) >= 2

    # Search query
    res_search = client.get("/api/v1/patients?search=Alice", headers=auth_headers)
    assert res_search.status_code == 200
    assert len(res_search.json()) == 1
    assert res_search.json()[0]["full_name"] == "Alice Wonder"


def test_get_and_update_patient_api(client, auth_headers, db_session):
    repo = PatientRepository(db_session)
    p = repo.create(Patient(full_name="Charlie Brown", date_of_birth=date(1992, 3, 3), gender="Male", phone="01933333333"))

    # Get by ID
    res_get = client.get(f"/api/v1/patients/{p.id}", headers=auth_headers)
    assert res_get.status_code == 200
    assert res_get.json()["full_name"] == "Charlie Brown"

    # Update
    update_payload = {"phone": "01944444444", "medical_history": "Mild gastritis"}
    res_update = client.put(f"/api/v1/patients/{p.id}", json=update_payload, headers=auth_headers)
    assert res_update.status_code == 200
    assert res_update.json()["phone"] == "01944444444"
    assert res_update.json()["medical_history"] == "Mild gastritis"


def test_delete_patient_api(client, auth_headers, db_session):
    repo = PatientRepository(db_session)
    p = repo.create(Patient(full_name="Delete Me", date_of_birth=date(1999, 9, 9), gender="Other", phone="01699999999"))

    res_del = client.delete(f"/api/v1/patients/{p.id}", headers=auth_headers)
    assert res_del.status_code == 200
    assert res_del.json()["message"] == f"Patient {p.id} successfully deleted"

    # Subsequent get returns 404
    res_get = client.get(f"/api/v1/patients/{p.id}", headers=auth_headers)
    assert res_get.status_code == 404
