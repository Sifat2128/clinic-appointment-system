from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import settings

openapi_tags = [
    {
        "name": "Auth & Users",
        "description": "Authentication, JWT token issuance, role-based access control (Admin, Doctor, Receptionist), and user provisioning.",
    },
    {
        "name": "Patients",
        "description": "Patient directory management, contact details, emergency information, and medical history notes.",
    },
    {
        "name": "Doctors & Schedules",
        "description": "Doctor profiles, specialization management, consultation fees, and recurring weekly availability schedules.",
    },
    {
        "name": "Appointments",
        "description": "Appointment booking with strict double-booking conflict prevention, status lifecycle transitions, and cancellation tracking.",
    },
    {
        "name": "Billing & Payments",
        "description": "Invoice creation with dynamic Discount Strategies (No Discount, Student, Senior Citizen, Insurance) and Payment Processing Factory (Cash, Card, Mobile Banking).",
    },
    {
        "name": "Reports & Analytics",
        "description": "Operational analytics including Daily Appointment Summaries and Period Financial Revenue Reports using the Report Generator Factory.",
    },
]

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Comprehensive RESTful API for outpatient clinic appointment scheduling, "
        "patient management, billing with Strategy & Factory design patterns, "
        "and operational analytics."
    ),
    contact={
        "name": "Clinic AMS Engineering Team",
        "url": "https://github.com/Sifat2128/clinic-appointment-system",
        "email": "sifatahasan2108@gmail.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=openapi_tags,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/v1/openapi.json"
)

# CORS Middleware for React Vite Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint to verify backend operational readiness."""
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
