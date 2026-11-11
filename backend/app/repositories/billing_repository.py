from datetime import date
from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.models.billing import Invoice, Payment
from backend.app.repositories.base import BaseRepository


class BillingRepository(BaseRepository[Invoice]):
    """Repository handling database operations for Invoices and Payments."""

    def __init__(self, db: Session):
        super().__init__(db, Invoice)

    def get_invoice_by_appointment(self, appointment_id: int) -> Optional[Invoice]:
        """Fetch invoice associated with a specific appointment."""
        return self.db.query(Invoice).filter(Invoice.appointment_id == appointment_id).first()

    def get_invoices_by_date_range(self, start_date: date, end_date: date) -> List[Invoice]:
        """Retrieve all invoices created within a date window."""
        return (
            self.db.query(Invoice)
            .filter(
                Invoice.created_at >= start_date,
                Invoice.created_at <= end_date,
            )
            .all()
        )

    def record_payment(self, payment: Payment) -> Payment:
        """Persist a newly processed payment transaction."""
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment

    def get_payments_by_invoice(self, invoice_id: int) -> List[Payment]:
        """Retrieve all payment records linked to an invoice."""
        return self.db.query(Payment).filter(Payment.invoice_id == invoice_id).all()
