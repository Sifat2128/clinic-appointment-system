from typing import Dict, List
from pydantic import BaseModel, Field


class DoctorWorkloadItem(BaseModel):
    doctor_id: int = Field(..., description="Doctor ID")
    specialization: str = Field(..., description="Specialty of the doctor")
    appointment_count: int = Field(..., description="Number of consultations booked")


class DailyAppointmentReportResponse(BaseModel):
    report_type: str = "daily_appointments"
    report_date: str = Field(..., description="Target date (YYYY-MM-DD)")
    total_appointments: int = Field(..., description="Total appointment bookings on date")
    status_breakdown: Dict[str, int] = Field(..., description="Count of appointments by status")
    doctor_workload: List[DoctorWorkloadItem] = Field(..., description="Consultation distribution across doctors")


class RevenueReportResponse(BaseModel):
    report_type: str = "revenue_analytics"
    start_date: str
    end_date: str
    paid_invoice_count: int
    total_gross_billed: float
    total_discounts_granted: float
    total_tax_collected: float
    total_net_revenue: float
    payment_breakdown: Dict[str, float]
