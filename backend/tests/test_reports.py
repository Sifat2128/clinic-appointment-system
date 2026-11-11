"""Tests for Reports Module and ReportGeneratorFactory (Daily Appointments and Revenue Analytics)."""
from datetime import date, datetime, time
import pytest
from backend.app.core.security import get_password_hash, create_access_token
from backend.app.models.user import User, UserRole
from backend.app.models.patient import Patient
from backend.app.models.doctor import Doctor
from backend.app.models.appointment import Appointment, AppointmentStatus
from backend.app.models.billing import Invoice, InvoiceStatus, Payment
from backend.app.patterns.factories.report_factory import (
    ReportGeneratorFactory,
    DailyAppointmentReportGenerator,
    RevenueReportGenerator,
)


@pytest.fixture
def admin_headers(db_session):
    user = User(
        email="admin.reports@clinic.com",
        full_name="Admin Analytics",
        hashed_password=get_password_hash("Admin123!"),
        role=UserRole.ADMIN.value,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token({"sub": user.email, "role": user.role, "user_id": user.id})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def seed_report_data(db_session):
    # Patient
    p1 = Patient(full_name="Patient One", date_of_birth=date(1990, 1, 1), gender="Male", phone="01711111111")
    p2 = Patient(full_name="Patient Two", date_of_birth=date(1985, 2, 2), gender="Female", phone="01822222222")
    db_session.add_all([p1, p2])
    db_session.commit()

    # Doctor
    doc_u = User(email="dr.report@clinic.com", full_name="Dr. Report Doc", hashed_password="x", role="doctor")
    db_session.add(doc_u)
    db_session.commit()
    doc = Doctor(user_id=doc_u.id, specialization="Neurology", consultation_fee=1500.0)
    db_session.add(doc)
    db_session.commit()

    # Target date: 2026-11-25
    target_d = date(2026, 11, 25)

    # 2 Appointments: 1 COMPLETED, 1 CANCELLED
    appt1 = Appointment(
        patient_id=p1.id, doctor_id=doc.id, appointment_date=target_d,
        appointment_time="09:00", status=AppointmentStatus.COMPLETED.value
    )
    appt2 = Appointment(
        patient_id=p2.id, doctor_id=doc.id, appointment_date=target_d,
        appointment_time="10:00", status=AppointmentStatus.CANCELLED.value,
        cancellation_reason="Patient sickness"
    )
    db_session.add_all([appt1, appt2])
    db_session.commit()

    # Invoice and Payment for appt1
    inv = Invoice(
        appointment_id=appt1.id, patient_id=p1.id, gross_amount=1500.0,
        discount_type="NONE", discount_amount=0.0, tax_amount=75.0,
        net_total=1575.0, status=InvoiceStatus.PAID.value,
        created_at=datetime.combine(target_d, time(10, 0)),
    )
    db_session.add(inv)
    db_session.commit()

    pay = Payment(invoice_id=inv.id, payment_method="CARD", amount_paid=1575.0, status="SUCCESS")
    db_session.add(pay)
    db_session.commit()

    return {"date": target_d, "doctor": doc}


def test_report_factory_instantiation():
    daily_gen = ReportGeneratorFactory.create_generator("daily_appointments")
    assert isinstance(daily_gen, DailyAppointmentReportGenerator)

    rev_gen = ReportGeneratorFactory.create_generator("revenue")
    assert isinstance(rev_gen, RevenueReportGenerator)

    with pytest.raises(ValueError, match="Unsupported report type"):
        ReportGeneratorFactory.create_generator("invalid_report_type")


def test_daily_appointment_report_generator(db_session, seed_report_data):
    target_d = seed_report_data["date"]
    generator = ReportGeneratorFactory.create_generator("daily_appointments")
    result = generator.generate(db_session, {"date": target_d})

    assert result["report_date"] == str(target_d)
    assert result["total_appointments"] == 2
    assert result["status_breakdown"]["COMPLETED"] == 1
    assert result["status_breakdown"]["CANCELLED"] == 1
    assert len(result["doctor_workload"]) >= 1


def test_revenue_report_generator(db_session, seed_report_data):
    target_d = seed_report_data["date"]
    generator = ReportGeneratorFactory.create_generator("revenue")
    result = generator.generate(db_session, {"start_date": target_d, "end_date": target_d})

    assert result["total_gross_billed"] >= 1500.0
    assert result["total_tax_collected"] >= 75.0
    assert result["total_net_revenue"] >= 1575.0
    assert "CARD" in result["payment_breakdown"]


def test_daily_appointments_api(client, admin_headers, seed_report_data):
    target_d = str(seed_report_data["date"])
    response = client.get(f"/api/v1/reports/daily-appointments?date={target_d}", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_appointments"] == 2
    assert data["status_breakdown"]["COMPLETED"] == 1


def test_revenue_report_api(client, admin_headers, seed_report_data):
    target_d = str(seed_report_data["date"])
    response = client.get(f"/api/v1/reports/revenue?start_date={target_d}&end_date={target_d}", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_net_revenue"] >= 1575.0
