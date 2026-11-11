"""Tests for Appointment Booking, Double-Booking Conflict Engine, Cancellation, and Email Mocking."""
from datetime import date
import pytest
from backend.app.core.security import get_password_hash, create_access_token
from backend.app.models.user import User, UserRole
from backend.app.models.patient import Patient
from backend.app.models.doctor import Doctor, DoctorSchedule
from backend.app.models.appointment import Appointment, AppointmentStatus
from backend.app.repositories.appointment_repository import AppointmentRepository
from backend.app.services.email_service import EmailService


@pytest.fixture
def receptionist_headers(db_session):
    user = User(
        email="receptionist.appt@clinic.com",
        full_name="Sarah Receptionist",
        hashed_password=get_password_hash("Recept123!"),
        role=UserRole.RECEPTIONIST.value,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token({"sub": user.email, "role": user.role, "user_id": user.id})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def setup_doctor_and_patient(db_session):
    # Setup Doctor User
    doc_user = User(
        email="dr.tanvir.appt@clinic.com",
        full_name="Dr. Tanvir Rahman",
        hashed_password=get_password_hash("Doc123!"),
        role=UserRole.DOCTOR.value,
        is_active=True,
    )
    db_session.add(doc_user)
    db_session.commit()
    db_session.refresh(doc_user)

    doctor = Doctor(
        user_id=doc_user.id,
        specialization="Cardiology",
        consultation_fee=1200.0,
        phone="+8801811223344",
        is_available=True,
    )
    db_session.add(doctor)
    db_session.commit()
    db_session.refresh(doctor)

    # Doctor Schedule on Mondays
    schedule = DoctorSchedule(
        doctor_id=doctor.id,
        day_of_week="Monday",
        start_time="09:00",
        end_time="12:00",
        slot_duration_minutes=30,
        max_patients=1,
    )
    db_session.add(schedule)

    # Setup Patient
    patient = Patient(
        full_name="Tariqul Islam",
        date_of_birth=date(1994, 6, 12),
        gender="Male",
        phone="+8801755667788",
        address="Mirpur, Dhaka",
    )
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)

    return {"doctor": doctor, "patient": patient}


def test_appointment_repository_conflict_checks(db_session, setup_doctor_and_patient):
    repo = AppointmentRepository(db_session)
    doctor = setup_doctor_and_patient["doctor"]
    patient = setup_doctor_and_patient["patient"]

    appt_date = date(2026, 11, 16)  # Monday
    appt_time = "09:30"

    # Initially no conflict
    assert repo.check_doctor_conflict(doctor.id, appt_date, appt_time) is False
    assert repo.check_patient_conflict(patient.id, appt_date, appt_time) is False

    # Create appointment
    appt = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        appointment_date=appt_date,
        appointment_time=appt_time,
        status=AppointmentStatus.SCHEDULED.value,
        reason="Chest discomfort checkup",
    )
    repo.create(appt)

    # Now both doctor and patient have conflict in this slot
    assert repo.check_doctor_conflict(doctor.id, appt_date, appt_time) is True
    assert repo.check_patient_conflict(patient.id, appt_date, appt_time) is True

    # Different time has no conflict
    assert repo.check_doctor_conflict(doctor.id, appt_date, "10:00") is False


def test_book_appointment_api_success(client, receptionist_headers, setup_doctor_and_patient, mocker):
    doctor = setup_doctor_and_patient["doctor"]
    patient = setup_doctor_and_patient["patient"]

    # Mock external email service with pytest-mock
    mock_send_email = mocker.patch.object(EmailService, "send_appointment_confirmation", return_value=True)

    payload = {
        "patient_id": patient.id,
        "doctor_id": doctor.id,
        "appointment_date": "2026-11-16",
        "appointment_time": "09:00",
        "reason": "General heart checkup",
    }
    response = client.post("/api/v1/appointments", json=payload, headers=receptionist_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "SCHEDULED"
    assert data["appointment_time"] == "09:00"

    # Verify mocked email service was called
    mock_send_email.assert_called_once()


def test_book_appointment_doctor_double_booking_conflict(client, receptionist_headers, setup_doctor_and_patient):
    doctor = setup_doctor_and_patient["doctor"]
    patient = setup_doctor_and_patient["patient"]

    # First booking
    payload = {
        "patient_id": patient.id,
        "doctor_id": doctor.id,
        "appointment_date": "2026-11-16",
        "appointment_time": "10:00",
        "reason": "Initial consultation",
    }
    res1 = client.post("/api/v1/appointments", json=payload, headers=receptionist_headers)
    assert res1.status_code == 201

    # Second booking for same doctor at same time with another patient
    res2 = client.post("/api/v1/appointments", json=payload, headers=receptionist_headers)
    assert res2.status_code == 409
    assert "Doctor is already booked" in res2.json()["detail"]


def test_cancel_appointment_api(client, receptionist_headers, setup_doctor_and_patient, mocker):
    doctor = setup_doctor_and_patient["doctor"]
    patient = setup_doctor_and_patient["patient"]

    mock_send_cancel_email = mocker.patch.object(EmailService, "send_cancellation_notification", return_value=True)

    # Book appointment
    payload = {
        "patient_id": patient.id,
        "doctor_id": doctor.id,
        "appointment_date": "2026-11-16",
        "appointment_time": "11:00",
        "reason": "Blood pressure review",
    }
    res_book = client.post("/api/v1/appointments", json=payload, headers=receptionist_headers)
    assert res_book.status_code == 201
    appt_id = res_book.json()["id"]

    # Cancel appointment
    cancel_payload = {"cancellation_reason": "Patient requested reschedule"}
    res_cancel = client.post(f"/api/v1/appointments/{appt_id}/cancel", json=cancel_payload, headers=receptionist_headers)
    assert res_cancel.status_code == 200
    data = res_cancel.json()
    assert data["status"] == "CANCELLED"
    assert data["cancellation_reason"] == "Patient requested reschedule"

    # Slot is now free again!
    res_rebook = client.post("/api/v1/appointments", json=payload, headers=receptionist_headers)
    assert res_rebook.status_code == 201

    # Verify mocked cancellation email was dispatched
    mock_send_cancel_email.assert_called_once()
