from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.patient import Patient
from backend.app.models.user import User
from backend.app.repositories.patient_repository import PatientRepository
from backend.app.schemas.patient import PatientCreate, PatientUpdate, PatientResponse
from backend.app.api.deps import get_current_user

router = APIRouter()


@router.post(
    "/patients",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Patients"],
    summary="Register New Patient",
    description="Registers a new patient record with demographic and emergency contact details.",
)
def create_patient(
    patient_in: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = PatientRepository(db)
    new_patient = Patient(**patient_in.model_dump())
    created = repo.create(new_patient)
    return PatientResponse.model_validate(created)


@router.get(
    "/patients",
    response_model=List[PatientResponse],
    tags=["Patients"],
    summary="List or Search Patients",
    description="Returns patient records with optional search filter by name or phone number.",
)
def list_patients(
    search: Optional[str] = Query(None, description="Search keyword for name or phone"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = PatientRepository(db)
    if search:
        patients = repo.search(search)
    else:
        patients = repo.get_all(skip=skip, limit=limit)
    return [PatientResponse.model_validate(p) for p in patients]


@router.get(
    "/patients/{patient_id}",
    response_model=PatientResponse,
    tags=["Patients"],
    summary="Get Patient by ID",
    description="Fetches comprehensive profile details and medical history for a single patient.",
)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = PatientRepository(db)
    patient = repo.get_by_id(patient_id)
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found.",
        )
    return PatientResponse.model_validate(patient)


@router.put(
    "/patients/{patient_id}",
    response_model=PatientResponse,
    tags=["Patients"],
    summary="Update Patient Information",
    description="Updates demographic info, phone number, address, or medical history.",
)
def update_patient(
    patient_id: int,
    patient_in: PatientUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = PatientRepository(db)
    update_data = patient_in.model_dump(exclude_unset=True)
    updated = repo.update(patient_id, update_data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found.",
        )
    return PatientResponse.model_validate(updated)


@router.delete(
    "/patients/{patient_id}",
    tags=["Patients"],
    summary="Delete Patient Record",
    description="Deletes a patient record from the database.",
)
def delete_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    repo = PatientRepository(db)
    success = repo.delete(patient_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient with ID {patient_id} not found.",
        )
    return {"status": "success", "message": f"Patient {patient_id} successfully deleted"}
