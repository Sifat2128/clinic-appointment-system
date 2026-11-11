from abc import ABC, abstractmethod
from datetime import date
from typing import Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.models.appointment import Appointment, AppointmentStatus
from backend.app.models.billing import Invoice, InvoiceStatus, Payment
from backend.app.models.doctor import Doctor


class IReportGenerator(ABC):
    """Abstract Product interface for operational and analytical clinic reports."""

    @abstractmethod
    def generate(self, db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        """Executes data extraction and aggregates report metrics."""
        pass


class DailyAppointmentReportGenerator(IReportGenerator):
    """Concrete Report Generator summarizing clinic appointment volume and doctor workloads for a single day."""

    def generate(self, db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        target_date: date = params.get("date") or date.today()
        if isinstance(target_date, str):
            target_date = date.fromisoformat(target_date)

        appointments = db.query(Appointment).filter(Appointment.appointment_date == target_date).all()
        total_count = len(appointments)

        # Status distribution
        status_counts = {
            AppointmentStatus.SCHEDULED.value: 0,
            AppointmentStatus.COMPLETED.value: 0,
            AppointmentStatus.CANCELLED.value: 0,
        }
        doctor_counts: Dict[int, int] = {}

        for appt in appointments:
            if appt.status in status_counts:
                status_counts[appt.status] += 1
            doctor_counts[appt.doctor_id] = doctor_counts.get(appt.doctor_id, 0) + 1

        # Populate doctor workload details
        doctor_workload = []
        for doc_id, count in doctor_counts.items():
            doctor = db.query(Doctor).filter(Doctor.id == doc_id).first()
            doctor_workload.append({
                "doctor_id": doc_id,
                "specialization": doctor.specialization if doctor else "General",
                "appointment_count": count,
            })

        return {
            "report_type": "daily_appointments",
            "report_date": str(target_date),
            "total_appointments": total_count,
            "status_breakdown": status_counts,
            "doctor_workload": doctor_workload,
        }


class RevenueReportGenerator(IReportGenerator):
    """Concrete Report Generator computing gross billing, discounts, taxes, and payment channels."""

    def generate(self, db: Session, params: Dict[str, Any]) -> Dict[str, Any]:
        start_date = params.get("start_date") or date.today()
        end_date = params.get("end_date") or date.today()

        from datetime import datetime, time

        if isinstance(start_date, str):
            start_date = date.fromisoformat(start_date)
        if isinstance(end_date, str):
            end_date = date.fromisoformat(end_date)

        start_dt = datetime.combine(start_date, time.min)
        end_dt = datetime.combine(end_date, time.max)

        # Query paid invoices in range
        invoices = (
            db.query(Invoice)
            .filter(
                Invoice.created_at >= start_dt,
                Invoice.created_at <= end_dt,
                Invoice.status == InvoiceStatus.PAID.value,
            )
            .all()
        )

        total_gross = sum(inv.gross_amount for inv in invoices)
        total_discount = sum(inv.discount_amount for inv in invoices)
        total_tax = sum(inv.tax_amount for inv in invoices)
        total_net = sum(inv.net_total for inv in invoices)

        # Payment channel distribution
        payment_breakdown: Dict[str, float] = {"CASH": 0.0, "CARD": 0.0, "MOBILE_BANKING": 0.0}
        for inv in invoices:
            for payment in inv.payments:
                method = payment.payment_method.upper()
                payment_breakdown[method] = payment_breakdown.get(method, 0.0) + payment.amount_paid

        return {
            "report_type": "revenue_analytics",
            "start_date": str(start_date),
            "end_date": str(end_date),
            "paid_invoice_count": len(invoices),
            "total_gross_billed": round(total_gross, 2),
            "total_discounts_granted": round(total_discount, 2),
            "total_tax_collected": round(total_tax, 2),
            "total_net_revenue": round(total_net, 2),
            "payment_breakdown": payment_breakdown,
        }


class ReportGeneratorFactory:
    """Creational Factory for report generator instances conforming to Open/Closed Principle."""

    _registry: Dict[str, type[IReportGenerator]] = {
        "daily_appointments": DailyAppointmentReportGenerator,
        "revenue": RevenueReportGenerator,
    }

    @classmethod
    def register_generator(cls, report_name: str, generator_cls: type[IReportGenerator]):
        """Registers a new report type for runtime extension."""
        cls._registry[report_name.lower().strip()] = generator_cls

    @classmethod
    def create_generator(cls, report_type: str) -> IReportGenerator:
        """Instantiates the report generator corresponding to requested type."""
        normalized = report_type.lower().strip()
        generator_class = cls._registry.get(normalized)
        if not generator_class:
            valid_types = list(cls._registry.keys())
            raise ValueError(f"Unsupported report type '{report_type}'. Supported types: {valid_types}")
        return generator_class()
