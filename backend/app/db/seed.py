"""Database Seeding Utility for Local Development and E2E Testing."""
from datetime import date
from sqlalchemy.orm import Session
from backend.app.core.security import get_password_hash
from backend.app.models.user import User, UserRole
from backend.app.models.doctor import Doctor, DoctorSchedule
from backend.app.models.patient import Patient


def seed_initial_data(db: Session) -> None:
    """Seeds the database with essential administrative, staff, doctor, and patient records."""
    # 1. Admin
    admin = db.query(User).filter(User.email == "admin@clinic.com").first()
    if not admin:
        admin = User(
            email="admin@clinic.com",
            full_name="System Administrator",
            hashed_password=get_password_hash("Admin123!"),
            role=UserRole.ADMIN.value,
            is_active=True,
        )
        db.add(admin)

    # 2. Receptionist
    receptionist = db.query(User).filter(User.email == "receptionist@clinic.com").first()
    if not receptionist:
        receptionist = User(
            email="receptionist@clinic.com",
            full_name="Front Desk Receptionist",
            hashed_password=get_password_hash("Reception123!"),
            role=UserRole.RECEPTIONIST.value,
            is_active=True,
        )
        db.add(receptionist)

    # 3. Doctor User
    doctor_user = db.query(User).filter(User.email == "dr.sarah@clinic.com").first()
    if not doctor_user:
        doctor_user = User(
            email="dr.sarah@clinic.com",
            full_name="Dr. Sarah Khan",
            hashed_password=get_password_hash("Doctor123!"),
            role=UserRole.DOCTOR.value,
            is_active=True,
        )
        db.add(doctor_user)
        db.commit()
        db.refresh(doctor_user)

    # 4. Doctor Profile
    doctor_profile = db.query(Doctor).filter(Doctor.user_id == doctor_user.id).first()
    if not doctor_profile:
        doctor_profile = Doctor(
            user_id=doctor_user.id,
            specialization="Cardiology",
            consultation_fee=150.0,
            phone="+1-555-0199",
            is_available=True,
        )
        db.add(doctor_profile)
        db.commit()
        db.refresh(doctor_profile)

    # 5. Doctor Weekly Schedules (Monday through Sunday)
    sched_count = db.query(DoctorSchedule).filter(DoctorSchedule.doctor_id == doctor_profile.id).count()
    if sched_count == 0:
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for day in days:
            schedule = DoctorSchedule(
                doctor_id=doctor_profile.id,
                day_of_week=day,
                start_time="09:00",
                end_time="17:00",
                slot_duration_minutes=30,
                max_patients=1,
            )
            db.add(schedule)

    # 6. Sample Patient
    patient = db.query(Patient).first()
    if not patient:
        patient = Patient(
            full_name="John Doe",
            date_of_birth=date(1990, 1, 1),
            gender="Male",
            phone="01711223344",
            address="Dhaka, Bangladesh",
            emergency_contact="01811223344",
            medical_history="None",
            allergies="None",
        )
        db.add(patient)

    db.commit()
