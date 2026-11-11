"""Tests for Doctor Profiles, Weekly Availability Schedules, and Slot Generation."""
import pytest
from backend.app.core.security import get_password_hash, create_access_token
from backend.app.models.user import User, UserRole
from backend.app.models.doctor import Doctor, DoctorSchedule
from backend.app.repositories.doctor_repository import DoctorRepository
from backend.app.services.schedule_service import generate_time_slots


@pytest.fixture
def admin_headers(db_session):
    admin = User(
        email="admin.doc@clinic.com",
        full_name="Admin Doc Manager",
        hashed_password=get_password_hash("Admin123!"),
        role=UserRole.ADMIN.value,
        is_active=True,
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    token = create_access_token({"sub": admin.email, "role": admin.role, "user_id": admin.id})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def doctor_user(db_session):
    user = User(
        email="doctor.tanvir@clinic.com",
        full_name="Dr. Tanvir Rahman",
        hashed_password=get_password_hash("Doc123!"),
        role=UserRole.DOCTOR.value,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def test_slot_generator_algorithm():
    # 09:00 to 11:00 with 30-minute intervals
    slots = generate_time_slots("09:00", "11:00", 30)
    assert slots == ["09:00", "09:30", "10:00", "10:30"]

    # 14:00 to 15:00 with 15-minute intervals
    slots_15 = generate_time_slots("14:00", "15:00", 15)
    assert slots_15 == ["14:00", "14:15", "14:30", "14:45"]


def test_doctor_repository_and_schedules(db_session, doctor_user):
    repo = DoctorRepository(db_session)
    doctor = Doctor(
        user_id=doctor_user.id,
        specialization="Cardiology",
        consultation_fee=1200.0,
        phone="+8801812345678",
        is_available=True,
    )
    created_doc = repo.create(doctor)
    assert created_doc.id is not None
    assert created_doc.specialization == "Cardiology"

    # Add weekly schedules
    sch_mon = DoctorSchedule(
        doctor_id=created_doc.id,
        day_of_week="Monday",
        start_time="09:00",
        end_time="13:00",
        slot_duration_minutes=30,
        max_patients=1,
    )
    repo.add_schedule(sch_mon)

    schedules = repo.get_schedules(created_doc.id)
    assert len(schedules) == 1
    assert schedules[0].day_of_week == "Monday"


def test_create_doctor_api(client, admin_headers, doctor_user):
    payload = {
        "user_id": doctor_user.id,
        "specialization": "Cardiology",
        "consultation_fee": 1200.0,
        "phone": "+8801812345678",
    }
    response = client.post("/api/v1/doctors", json=payload, headers=admin_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["specialization"] == "Cardiology"
    assert data["consultation_fee"] == 1200.0


def test_add_doctor_schedule_api(client, admin_headers, db_session, doctor_user):
    repo = DoctorRepository(db_session)
    doc = repo.create(Doctor(user_id=doctor_user.id, specialization="Pediatrics", consultation_fee=1000.0))

    schedule_payload = {
        "day_of_week": "Tuesday",
        "start_time": "10:00",
        "end_time": "14:00",
        "slot_duration_minutes": 30,
        "max_patients": 1,
    }
    response = client.post(f"/api/v1/doctors/{doc.id}/schedules", json=schedule_payload, headers=admin_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["day_of_week"] == "Tuesday"
    assert data["start_time"] == "10:00"

    # Invalid schedule: end time <= start time
    invalid_payload = {
        "day_of_week": "Wednesday",
        "start_time": "14:00",
        "end_time": "10:00",
        "slot_duration_minutes": 30,
        "max_patients": 1,
    }
    invalid_res = client.post(f"/api/v1/doctors/{doc.id}/schedules", json=invalid_payload, headers=admin_headers)
    assert invalid_res.status_code == 400


def test_get_doctor_slots_api(client, admin_headers, db_session, doctor_user):
    repo = DoctorRepository(db_session)
    doc = repo.create(Doctor(user_id=doctor_user.id, specialization="Dermatology", consultation_fee=1100.0))
    repo.add_schedule(DoctorSchedule(
        doctor_id=doc.id,
        day_of_week="Monday",
        start_time="09:00",
        end_time="11:00",
        slot_duration_minutes=30,
        max_patients=1,
    ))

    # Query slots for Monday
    res = client.get(f"/api/v1/doctors/{doc.id}/slots?day_of_week=Monday", headers=admin_headers)
    assert res.status_code == 200
    slots = res.json()["slots"]
    assert slots == ["09:00", "09:30", "10:00", "10:30"]
