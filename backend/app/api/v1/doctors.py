from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.user import User, UserRole
from backend.app.models.doctor import Doctor, DoctorSchedule
from backend.app.repositories.doctor_repository import DoctorRepository
from backend.app.repositories.user_repository import UserRepository
from backend.app.repositories.appointment_repository import AppointmentRepository
from backend.app.schemas.doctor import (
    DoctorCreate, DoctorUpdate, DoctorResponse,
    DoctorScheduleCreate, DoctorScheduleResponse, DoctorSlotsResponse
)
from backend.app.services.schedule_service import generate_time_slots
from backend.app.api.deps import get_current_user, require_roles

router = APIRouter()


@router.post(
    "/doctors",
    response_model=DoctorResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Doctors & Schedules"],
    summary="Create Doctor Profile",
    description="Registers a new doctor profile linked to a staff user account. Restricted to Administrators.",
)
def create_doctor(
    doctor_in: DoctorCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_roles([UserRole.ADMIN.value])),
):
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(doctor_in.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User account with ID {doctor_in.user_id} does not exist.",
        )

    doc_repo = DoctorRepository(db)
    existing_doc = doc_repo.get_by_user_id(doctor_in.user_id)
    if existing_doc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Doctor profile for user ID {doctor_in.user_id} already exists.",
        )

    new_doc = Doctor(
        user_id=doctor_in.user_id,
        specialization=doctor_in.specialization,
        consultation_fee=doctor_in.consultation_fee,
        phone=doctor_in.phone,
        is_available=doctor_in.is_available,
    )
    created = doc_repo.create(new_doc)
    return DoctorResponse.model_validate(created)


@router.get(
    "/doctors",
    response_model=List[DoctorResponse],
    tags=["Doctors & Schedules"],
    summary="List Doctors",
    description="Returns all active doctor profiles with optional filter by specialization.",
)
def list_doctors(
    specialization: Optional[str] = Query(None, description="Filter by medical specialty"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc_repo = DoctorRepository(db)
    query = db.query(Doctor)
    if specialization:
        query = query.filter(Doctor.specialization.ilike(f"%{specialization}%"))
    doctors = query.offset(skip).limit(limit).all()
    return [DoctorResponse.model_validate(d) for d in doctors]


@router.get(
    "/doctors/{doctor_id}",
    response_model=DoctorResponse,
    tags=["Doctors & Schedules"],
    summary="Get Doctor Profile",
    description="Fetches detailed doctor profile along with configured weekly schedules.",
)
def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc_repo = DoctorRepository(db)
    doctor = doc_repo.get_by_id(doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with ID {doctor_id} not found.",
        )
    return DoctorResponse.model_validate(doctor)


@router.post(
    "/doctors/{doctor_id}/schedules",
    response_model=DoctorScheduleResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Doctors & Schedules"],
    summary="Configure Doctor Weekly Schedule Slot",
    description="Adds a recurring availability window (Day, Start Time, End Time, Slot Duration).",
)
def add_schedule(
    doctor_id: int,
    schedule_in: DoctorScheduleCreate,
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_roles([UserRole.ADMIN.value])),
):
    doc_repo = DoctorRepository(db)
    doctor = doc_repo.get_by_id(doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with ID {doctor_id} not found.",
        )

    # Validate that end_time is strictly after start_time
    slots = generate_time_slots(schedule_in.start_time, schedule_in.end_time, schedule_in.slot_duration_minutes)
    if not slots:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid schedule timing: end_time ({schedule_in.end_time}) must be after start_time ({schedule_in.start_time}).",
        )

    new_schedule = DoctorSchedule(
        doctor_id=doctor_id,
        day_of_week=schedule_in.day_of_week,
        start_time=schedule_in.start_time,
        end_time=schedule_in.end_time,
        slot_duration_minutes=schedule_in.slot_duration_minutes,
        max_patients=schedule_in.max_patients,
    )
    saved_schedule = doc_repo.add_schedule(new_schedule)
    return DoctorScheduleResponse.model_validate(saved_schedule)


@router.get(
    "/doctors/{doctor_id}/slots",
    response_model=DoctorSlotsResponse,
    tags=["Doctors & Schedules"],
    summary="Get Available Time Slots for Doctor",
    description="Calculates discrete appointment consultation slots for a specific day of the week.",
)
def get_doctor_slots(
    doctor_id: int,
    day_of_week: str = Query(..., description="Day of week (e.g. Monday, Tuesday)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc_repo = DoctorRepository(db)
    doctor = doc_repo.get_by_id(doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with ID {doctor_id} not found.",
        )

    schedule = doc_repo.get_schedule_by_day(doctor_id, day_of_week)
    if not schedule:
        return DoctorSlotsResponse(doctor_id=doctor_id, day_of_week=day_of_week, slots=[])

    slots = generate_time_slots(schedule.start_time, schedule.end_time, schedule.slot_duration_minutes)
    return DoctorSlotsResponse(doctor_id=doctor_id, day_of_week=day_of_week, slots=slots)


@router.get(
    "/doctors/{doctor_id}/available-slots",
    tags=["Doctors & Schedules"],
    summary="Get Available Real-Time Slots for Doctor by Date",
    description="Calculates real-time availability for a doctor on a specific date, excluding already booked slots.",
)
def get_available_slots_by_date(
    doctor_id: int,
    date: str = Query(..., description="Date formatted as YYYY-MM-DD"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doc_repo = DoctorRepository(db)
    doctor = doc_repo.get_by_id(doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with ID {doctor_id} not found.",
        )

    try:
        parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Expected YYYY-MM-DD.",
        )

    day_name = parsed_date.strftime("%A")  # e.g. "Monday"
    schedule = doc_repo.get_schedule_by_day(doctor_id, day_name)
    if not schedule:
        return []

    time_slots = generate_time_slots(schedule.start_time, schedule.end_time, schedule.slot_duration_minutes)

    apt_repo = AppointmentRepository(db)
    booked_appointments = apt_repo.get_by_doctor_and_date(doctor_id, parsed_date)
    booked_times = {
        apt.appointment_time[:5]
        for apt in booked_appointments
        if apt.status != "CANCELLED"
    }

    available = []
    for t in time_slots:
        slot_clean = t[:5]
        if slot_clean not in booked_times:
            available.append({
                "slot_start": slot_clean,
                "display_time": slot_clean,
                "is_available": True,
            })

    return available
