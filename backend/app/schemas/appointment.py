from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from backend.app.models.appointment import AppointmentStatus


class AppointmentBase(BaseModel):
    patient_id: int = Field(..., description="Target patient ID")
    doctor_id: int = Field(..., description="Target doctor ID")
    appointment_date: date = Field(..., description="Appointment date (YYYY-MM-DD)")
    appointment_time: str = Field(..., description="Slot time in HH:MM format")
    reason: Optional[str] = Field(None, max_length=255, description="Medical consultation reason")


class AppointmentCreate(AppointmentBase):
    pass


class AppointmentCancel(BaseModel):
    cancellation_reason: str = Field(..., min_length=3, description="Required reason for appointment cancellation")


class AppointmentResponse(AppointmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    cancellation_reason: Optional[str] = None
    created_at: datetime
