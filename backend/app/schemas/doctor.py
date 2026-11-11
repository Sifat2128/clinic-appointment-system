from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class DoctorScheduleBase(BaseModel):
    day_of_week: str = Field(..., description="Day of week (Monday-Sunday)")
    start_time: str = Field(..., description="Start time in HH:MM format")
    end_time: str = Field(..., description="End time in HH:MM format")
    slot_duration_minutes: int = Field(default=30, description="Duration per patient slot")
    max_patients: int = Field(default=1, description="Max patient count per slot")


class DoctorScheduleCreate(DoctorScheduleBase):
    pass


class DoctorScheduleResponse(DoctorScheduleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    doctor_id: int


class DoctorBase(BaseModel):
    specialization: str = Field(..., description="Medical specialization field")
    consultation_fee: float = Field(default=1000.0, description="Standard consultation fee")
    phone: Optional[str] = Field(None, description="Contact telephone")
    is_available: bool = Field(default=True, description="Doctor actively on duty")


class DoctorCreate(DoctorBase):
    user_id: int = Field(..., description="Linked staff User ID")


class DoctorUpdate(BaseModel):
    specialization: Optional[str] = None
    consultation_fee: Optional[float] = None
    phone: Optional[str] = None
    is_available: Optional[bool] = None


class DoctorResponse(DoctorBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    schedules: List[DoctorScheduleResponse] = []


class DoctorSlotsResponse(BaseModel):
    doctor_id: int
    day_of_week: str
    slots: List[str]
