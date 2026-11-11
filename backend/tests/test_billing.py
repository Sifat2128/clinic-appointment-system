"""Tests for Billing, Strategy Pattern (Discounts), Factory Pattern (Payment Processors), and Payment Gateway Mocking."""
from datetime import date
import pytest
from backend.app.core.security import get_password_hash, create_access_token
from backend.app.models.user import User, UserRole
from backend.app.models.patient import Patient
from backend.app.models.doctor import Doctor
from backend.app.models.appointment import Appointment, AppointmentStatus
from backend.app.models.billing import Invoice, InvoiceStatus, Payment
from backend.app.repositories.billing_repository import BillingRepository
from backend.app.patterns.strategies.discount_strategy import (
    NoDiscountStrategy,
    StudentDiscountStrategy,
    SeniorCitizenDiscountStrategy,
    InsuranceDiscountStrategy,
    BillingCalculationEngine,
)
from backend.app.patterns.factories.payment_factory import (
    PaymentProcessorFactory,
    CashPaymentProcessor,
    CardPaymentProcessor,
    MobileBankingPaymentProcessor,
)


@pytest.fixture
def cashier_headers(db_session):
    user = User(
        email="cashier.billing@clinic.com",
        full_name="Cashier John",
        hashed_password=get_password_hash("Cashier123!"),
        role=UserRole.RECEPTIONIST.value,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    token = create_access_token({"sub": user.email, "role": user.role, "user_id": user.id})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def setup_appointment(db_session):
    # Patient
    patient = Patient(
        full_name="Salma Begum",
        date_of_birth=date(1955, 3, 10),  # Senior citizen
        gender="Female",
        phone="+8801722334455",
    )
    db_session.add(patient)
    db_session.commit()
    db_session.refresh(patient)

    # Doctor User
    doc_user = User(
        email="dr.hasan@clinic.com",
        full_name="Dr. Hasan Mahmud",
        hashed_password=get_password_hash("Doc123!"),
        role=UserRole.DOCTOR.value,
        is_active=True,
    )
    db_session.add(doc_user)
    db_session.commit()
    db_session.refresh(doc_user)

    doctor = Doctor(
        user_id=doc_user.id,
        specialization="Orthopedics",
        consultation_fee=1000.0,
    )
    db_session.add(doctor)
    db_session.commit()
    db_session.refresh(doctor)

    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        appointment_date=date(2026, 11, 20),
        appointment_time="10:00",
        status=AppointmentStatus.SCHEDULED.value,
    )
    db_session.add(appointment)
    db_session.commit()
    db_session.refresh(appointment)

    return {"patient": patient, "doctor": doctor, "appointment": appointment}


def test_strategy_pattern_discount_calculations():
    engine = BillingCalculationEngine()
    gross_fee = 1000.0

    # 1. No Discount (0%)
    res_none = engine.calculate_bill(gross_fee, NoDiscountStrategy())
    assert res_none["discount_amount"] == 0.0
    assert res_none["taxable_subtotal"] == 1000.0
    assert res_none["tax_amount"] == 50.0  # 5% tax
    assert res_none["net_total"] == 1050.0

    # 2. Student Discount (18% resolved concession rate)
    res_student = engine.calculate_bill(gross_fee, StudentDiscountStrategy())
    assert res_student["discount_amount"] == 180.0
    assert res_student["taxable_subtotal"] == 820.0
    assert res_student["tax_amount"] == 41.0
    assert res_student["net_total"] == 861.0

    # 3. Senior Citizen Discount (20%)
    res_senior = engine.calculate_bill(gross_fee, SeniorCitizenDiscountStrategy())
    assert res_senior["discount_amount"] == 200.0
    assert res_senior["taxable_subtotal"] == 800.0
    assert res_senior["tax_amount"] == 40.0
    assert res_senior["net_total"] == 840.0

    # 4. Insurance / Corporate Discount (30%)
    res_insurance = engine.calculate_bill(gross_fee, InsuranceDiscountStrategy())
    assert res_insurance["discount_amount"] == 300.0
    assert res_insurance["taxable_subtotal"] == 700.0
    assert res_insurance["tax_amount"] == 35.0
    assert res_insurance["net_total"] == 735.0


def test_factory_pattern_payment_processors():
    # Factory instantiates correct processor subclasses
    cash_proc = PaymentProcessorFactory.create_processor("CASH")
    assert isinstance(cash_proc, CashPaymentProcessor)

    card_proc = PaymentProcessorFactory.create_processor("CARD")
    assert isinstance(card_proc, CardPaymentProcessor)

    mobile_proc = PaymentProcessorFactory.create_processor("MOBILE_BANKING")
    assert isinstance(mobile_proc, MobileBankingPaymentProcessor)

    with pytest.raises(ValueError, match="Unsupported payment method"):
        PaymentProcessorFactory.create_processor("BITCOIN")


def test_create_invoice_api_with_discount_strategy(client, cashier_headers, setup_appointment):
    appt = setup_appointment["appointment"]
    patient = setup_appointment["patient"]

    payload = {
        "appointment_id": appt.id,
        "patient_id": patient.id,
        "discount_type": "STUDENT",
    }
    response = client.post("/api/v1/billing/invoices", json=payload, headers=cashier_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["gross_amount"] == 1000.0
    assert data["discount_type"] == "STUDENT"
    assert data["discount_amount"] == 180.0
    assert data["net_total"] == 861.0
    assert data["status"] == "PENDING"


def test_process_card_payment_with_gateway_mock(client, cashier_headers, setup_appointment, mocker):
    appt = setup_appointment["appointment"]
    patient = setup_appointment["patient"]

    # Create Invoice first
    res_inv = client.post(
        "/api/v1/billing/invoices",
        json={"appointment_id": appt.id, "patient_id": patient.id, "discount_type": "NONE"},
        headers=cashier_headers,
    )
    assert res_inv.status_code == 201
    invoice_id = res_inv.json()["id"]

    # Mock external card processing gateway
    mock_gateway = mocker.patch(
        "backend.app.patterns.factories.payment_factory.CardPaymentProcessor._simulate_bank_gateway",
        return_value={"gateway_status": "APPROVED", "auth_code": "AUTH-889922"},
    )

    pay_payload = {
        "payment_method": "CARD",
        "amount_paid": 1050.0,
        "transaction_ref": "CARD-REF-992384",
    }
    response = client.post(f"/api/v1/billing/invoices/{invoice_id}/pay", json=pay_payload, headers=cashier_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["invoice"]["status"] == "PAID"
    assert data["payment"]["payment_method"] == "CARD"
    assert data["payment"]["status"] == "SUCCESS"

    mock_gateway.assert_called_once()

    # Re-paying already paid invoice fails
    res_repay = client.post(f"/api/v1/billing/invoices/{invoice_id}/pay", json=pay_payload, headers=cashier_headers)
    assert res_repay.status_code == 400
    assert "already settled" in res_repay.json()["detail"]
