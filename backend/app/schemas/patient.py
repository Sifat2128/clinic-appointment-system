from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class PatientBase(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255, description="Patient full name")
    date_of_birth: date = Field(..., description="Date of birth (YYYY-MM-DD)")
    gender: str = Field(..., description="Gender (Male, Female, Other)")
    phone: str = Field(..., min_length=5, max_length=50, description="Contact phone number")
    address: Optional[str] = Field(None, max_length=255, description="Residential address")
    emergency_contact: Optional[str] = Field(None, max_length=50, description="Emergency phone number")
    medical_history: Optional[str] = Field(None, description="Pre-existing medical conditions")
    allergies: Optional[str] = Field(None, description="Known drug and environmental allergies")


class PatientCreate(PatientBase):
    pass


class PatientUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    phone: Optional[str] = Field(None, min_length=5, max_length=50)
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    medical_history: Optional[str] = None
    allergies: Optional[str] = None


class PatientResponse(PatientBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
