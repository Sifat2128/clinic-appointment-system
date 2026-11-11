from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.appointment import Appointment, AppointmentStatus
from backend.app.repositories.appointment_repository import AppointmentRepository
from backend.app.repositories.doctor_repository import DoctorRepository
from backend.app.repositories.patient_repository import PatientRepository
from backend.app.schemas.appointment import AppointmentCreate, AppointmentCancel, AppointmentResponse
from backend.app.services.email_service import EmailService
from backend.app.api.deps import get_current_user

router = APIRouter()


@router.post(
    "/appointments",
    response_model=AppointmentResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Appointments"],
    summary="Book New Appointment",
    description="Schedules a consultation slot for a patient with double-booking and overlap conflict prevention.",
    responses={
        201: {"description": "Appointment scheduled successfully"},
        404: {"description": "Patient or Doctor not found"},
        409: {"description": "Conflict: Doctor or patient already booked in this slot"},
    }
)
def book_appointment(
    appt_in: AppointmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    patient_repo = PatientRepository(db)
    patient = patient_repo.get_by_id(appt_in.patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {appt_in.patient_id} does not exist.",
        )

    doc_repo = DoctorRepository(db)
    doctor = doc_repo.get_by_id(appt_in.doctor_id)
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Doctor with ID {appt_in.doctor_id} does not exist.",
        )

    appt_repo = AppointmentRepository(db)
    # Check doctor double booking
    if appt_repo.check_doctor_conflict(appt_in.doctor_id, appt_in.appointment_date, appt_in.appointment_time):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Doctor is already booked for this time slot.",
        )

    # Check patient overlap
    if appt_repo.check_patient_conflict(appt_in.patient_id, appt_in.appointment_date, appt_in.appointment_time):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Patient already has a conflicting appointment at this time.",
        )

    new_appt = Appointment(
        patient_id=appt_in.patient_id,
        doctor_id=appt_in.doctor_id,
        appointment_date=appt_in.appointment_date,
        appointment_time=appt_in.appointment_time,
        status=AppointmentStatus.SCHEDULED.value,
        reason=appt_in.reason,
    )
    created = appt_repo.create(new_appt)

    # Send transactional confirmation notification (mocked in tests)
    EmailService.send_appointment_confirmation(
        to_email=patient.phone,
        doctor_name=doctor.specialization,
        date_str=str(created.appointment_date),
        time_str=created.appointment_time,
    )

    return AppointmentResponse.model_validate(created)


@router.get(
    "/appointments",
    response_model=List[AppointmentResponse],
    tags=["Appointments"],
    summary="List Appointments",
    description="Retrieves clinic appointments with optional date, doctor, or patient filters.",
)
def list_appointments(
    appointment_date: Optional[date] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    doctor_id: Optional[int] = Query(None, description="Filter by doctor ID"),
    patient_id: Optional[int] = Query(None, description="Filter by patient ID"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Appointment)
    if appointment_date:
        query = query.filter(Appointment.appointment_date == appointment_date)
    if doctor_id:
        query = query.filter(Appointment.doctor_id == doctor_id)
    if patient_id:
        query = query.filter(Appointment.patient_id == patient_id)

    appts = query.offset(skip).limit(limit).all()
    return [AppointmentResponse.model_validate(a) for a in appts]


@router.get(
    "/appointments/{appointment_id}",
    response_model=AppointmentResponse,
    tags=["Appointments"],
    summary="Get Appointment Details",
    description="Retrieves a single appointment record by ID.",
)
def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    appt_repo = AppointmentRepository(db)
    appt = appt_repo.get_by_id(appointment_id)
    if not appt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment with ID {appointment_id} not found.",
        )
    return AppointmentResponse.model_validate(appt)


@router.post(
    "/appointments/{appointment_id}/cancel",
    response_model=AppointmentResponse,
    tags=["Appointments"],
    summary="Cancel Appointment",
    description="Cancels a scheduled appointment, recording the reason and releasing the consultation slot.",
    responses={
        200: {"description": "Appointment successfully cancelled"},
        400: {"description": "Bad Request: Appointment cannot be cancelled"},
        404: {"description": "Appointment not found"},
    }
)
def cancel_appointment(
    appointment_id: int,
    cancel_in: AppointmentCancel,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    appt_repo = AppointmentRepository(db)
    appt = appt_repo.get_by_id(appointment_id)
    if not appt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Appointment with ID {appointment_id} not found.",
        )

    if appt.status in [AppointmentStatus.CANCELLED.value, AppointmentStatus.COMPLETED.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel appointment with status '{appt.status}'.",
        )

    updated = appt_repo.update(appointment_id, {
        "status": AppointmentStatus.CANCELLED.value,
        "cancellation_reason": cancel_in.cancellation_reason,
    })

    # Dispatch notification (mocked in tests)
    EmailService.send_cancellation_notification(
        to_email=str(appt.patient_id),
        doctor_name=str(appt.doctor_id),
        date_str=str(appt.appointment_date),
        time_str=appt.appointment_time,
        reason=cancel_in.cancellation_reason,
    )

    return AppointmentResponse.model_validate(updated)
