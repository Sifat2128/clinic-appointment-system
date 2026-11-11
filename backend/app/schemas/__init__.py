from backend.app.schemas.user import UserBase, UserCreate, UserUpdate, UserResponse, UserLogin, TokenResponse, TokenPayload
from backend.app.schemas.patient import PatientBase, PatientCreate, PatientUpdate, PatientResponse
from backend.app.schemas.doctor import (
    DoctorBase, DoctorCreate, DoctorUpdate, DoctorResponse,
    DoctorScheduleBase, DoctorScheduleCreate, DoctorScheduleResponse, DoctorSlotsResponse
)

__all__ = [
    "UserBase", "UserCreate", "UserUpdate", "UserResponse", "UserLogin", "TokenResponse", "TokenPayload",
    "PatientBase", "PatientCreate", "PatientUpdate", "PatientResponse",
    "DoctorBase", "DoctorCreate", "DoctorUpdate", "DoctorResponse",
    "DoctorScheduleBase", "DoctorScheduleCreate", "DoctorScheduleResponse", "DoctorSlotsResponse"
]
