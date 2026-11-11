from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class InvoiceCreate(BaseModel):
    appointment_id: int = Field(..., description="Linked Appointment ID")
    patient_id: int = Field(..., description="Patient ID")
    discount_type: str = Field(default="NONE", description="Discount Strategy category: NONE, STUDENT, SENIOR_CITIZEN, INSURANCE")


class PaymentCreate(BaseModel):
    payment_method: str = Field(..., description="Payment channel: CASH, CARD, MOBILE_BANKING")
    amount_paid: float = Field(..., description="Monetary amount tendered/charged")
    transaction_ref: Optional[str] = Field(None, description="External transaction or card receipt reference")


class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    invoice_id: int
    payment_method: str
    amount_paid: float
    transaction_ref: Optional[str] = None
    status: str
    payment_date: datetime


class InvoiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    appointment_id: int
    patient_id: int
    gross_amount: float
    discount_type: str
    discount_amount: float
    tax_amount: float
    net_total: float
    status: str
    created_at: datetime
    payments: List[PaymentResponse] = []


class PaymentCheckoutResponse(BaseModel):
    message: str = "Payment successfully processed"
    invoice: InvoiceResponse
    payment: PaymentResponse
