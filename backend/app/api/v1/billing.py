from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.billing import Invoice, InvoiceStatus, Payment
from backend.app.repositories.billing_repository import BillingRepository
from backend.app.repositories.appointment_repository import AppointmentRepository
from backend.app.repositories.doctor_repository import DoctorRepository
from backend.app.schemas.billing import (
    InvoiceCreate, InvoiceResponse, PaymentCreate, PaymentCheckoutResponse, PaymentResponse
)
from backend.app.patterns.strategies.discount_strategy import (
    get_discount_strategy, BillingCalculationEngine
)
from backend.app.patterns.factories.payment_factory import PaymentProcessorFactory
from backend.app.api.deps import get_current_user

router = APIRouter()


@router.post(
    "/billing/invoices",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Billing & Payments"],
    summary="Generate Consultation Invoice",
    description="Generates an invoice for an appointment applying the specified Discount Strategy (NONE, STUDENT, SENIOR_CITIZEN, INSURANCE).",
    responses={
        201: {"description": "Invoice generated"},
        404: {"description": "Appointment not found"},
        409: {"description": "Invoice for this appointment already exists"},
    }
)
def create_invoice(
    invoice_in: InvoiceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    appt_repo = AppointmentRepository(db)
    appt = appt_repo.get_by_id(invoice_in.appointment_id)
    if not appt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment with ID {invoice_in.appointment_id} does not exist.",
        )

    billing_repo = BillingRepository(db)
    existing_inv = billing_repo.get_invoice_by_appointment(invoice_in.appointment_id)
    if existing_inv:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Invoice for appointment ID {invoice_in.appointment_id} already exists.",
        )

    doc_repo = DoctorRepository(db)
    doctor = doc_repo.get_by_id(appt.doctor_id)
    gross_fee = doctor.consultation_fee if doctor else 1000.0

    # Execute Strategy Pattern for Discount Calculation
    strategy = get_discount_strategy(invoice_in.discount_type)
    calc_engine = BillingCalculationEngine()
    calc_result = calc_engine.calculate_bill(gross_fee, strategy)

    new_invoice = Invoice(
        appointment_id=invoice_in.appointment_id,
        patient_id=invoice_in.patient_id,
        gross_amount=calc_result["gross_amount"],
        discount_type=calc_result["discount_type"],
        discount_amount=calc_result["discount_amount"],
        tax_amount=calc_result["tax_amount"],
        net_total=calc_result["net_total"],
        status=InvoiceStatus.PENDING.value,
    )
    created_inv = billing_repo.create(new_invoice)
    return InvoiceResponse.model_validate(created_inv)


@router.get(
    "/billing/invoices",
    response_model=List[InvoiceResponse],
    tags=["Billing & Payments"],
    summary="List Invoices",
    description="Lists clinic invoices with optional status filter.",
)
def list_invoices(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: PENDING, PAID, REFUNDED"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Invoice)
    if status_filter:
        query = query.filter(Invoice.status == status_filter.upper())
    invoices = query.offset(skip).limit(limit).all()
    return [InvoiceResponse.model_validate(inv) for inv in invoices]


@router.get(
    "/billing/invoices/{invoice_id}",
    response_model=InvoiceResponse,
    tags=["Billing & Payments"],
    summary="Get Invoice by ID",
    description="Retrieves a single invoice record including applied discounts and payment transactions.",
)
def get_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    billing_repo = BillingRepository(db)
    invoice = billing_repo.get_by_id(invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice with ID {invoice_id} not found.",
        )
    return InvoiceResponse.model_validate(invoice)


@router.post(
    "/billing/invoices/{invoice_id}/pay",
    response_model=PaymentCheckoutResponse,
    tags=["Billing & Payments"],
    summary="Process Invoice Payment",
    description="Executes payment using the PaymentProcessorFactory (CASH, CARD, MOBILE_BANKING) and transitions invoice to PAID.",
    responses={
        200: {"description": "Payment approved and settled"},
        400: {"description": "Bad Request: Invoice already settled or invalid payment"},
        404: {"description": "Invoice not found"},
    }
)
def process_invoice_payment(
    invoice_id: int,
    payment_in: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    billing_repo = BillingRepository(db)
    invoice = billing_repo.get_by_id(invoice_id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice with ID {invoice_id} not found.",
        )

    if invoice.status == InvoiceStatus.PAID.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice is already settled.",
        )

    # Instantiate Processor via Factory Pattern
    try:
        processor = PaymentProcessorFactory.create_processor(payment_in.payment_method)
        payment_entity = processor.process_payment(
            invoice=invoice,
            amount=payment_in.amount_paid,
            transaction_ref=payment_in.transaction_ref,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    # Persist payment and update invoice state
    recorded_payment = billing_repo.record_payment(payment_entity)
    billing_repo.update(invoice_id, {"status": InvoiceStatus.PAID.value})
    db.refresh(invoice)

    return PaymentCheckoutResponse(
        message="Payment successfully processed",
        invoice=InvoiceResponse.model_validate(invoice),
        payment=PaymentResponse.model_validate(recorded_payment),
    )
