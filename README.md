# Clinic Appointment Management System

[![Continuous Integration](https://github.com/Sifat2128/clinic-appointment-system/actions/workflows/ci.yml/badge.svg)](https://github.com/Sifat2128/clinic-appointment-system/actions/workflows/ci.yml)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI_0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/Frontend-React_19_+_Vite-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![Python](https://img.shields.io/badge/Python-3.11%20%7C%203.13-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Coverage](https://img.shields.io/badge/Coverage-90%25-brightgreen.svg)](docs/coverage-summary.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An enterprise-grade, full-stack **Clinic Appointment Management System** designed and built for a university Software Engineering Sessional course. The system facilitates end-to-end outpatient healthcare administration—from multi-role authentication and demographic tracking to conflict-free appointment scheduling, Strategy-pattern discount billing, Factory-pattern multi-channel payments, and clinical operations analytics.

---

## 1. System Architecture & Monorepo Layout

```
clinic-appointment-system/
├── .github/
│   └── workflows/
│       └── ci.yml                     # Multi-runtime CI workflow (Python 3.11 + Node 20)
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/                    # Modular REST API endpoints under /api/v1
│   │   │   │   ├── auth.py            # JWT authentication & RBAC user provisioning
│   │   │   │   ├── patients.py        # Patient demographic registration & search
│   │   │   │   ├── doctors.py         # Specialist profiles & weekly schedule slots
│   │   │   │   ├── appointments.py    # Booking with strict conflict prevention
│   │   │   │   ├── billing.py         # Invoice settlement with Strategy & Factory
│   │   │   │   └── reports.py         # Operations summaries & revenue analytics
│   │   │   └── deps.py                # Database and OAuth2 security dependencies
│   │   ├── core/                      # Password hashing (bcrypt) & JWT issuance
│   │   ├── db/                        # Seed data utility for instant demo bootstrapping
│   │   ├── models/                    # SQLAlchemy persistent domain entities
│   │   ├── patterns/                  # GoF Design Pattern Implementations
│   │   │   ├── factories/             # Creational: PaymentProcessorFactory, ReportFactory
│   │   │   └── strategies/            # Behavioral: IDiscountStrategy implementations
│   │   ├── repositories/              # Structural: Generic BaseRepository & concrete repos
│   │   ├── schemas/                   # Pydantic v2 data transfer objects & validation
│   │   ├── services/                  # Schedule slot generation & mock email relays
│   │   ├── config.py                  # Environment settings & CORS definitions
│   │   ├── database.py                # SQLite engine with foreign key pragmas
│   │   └── main.py                    # FastAPI root with customized OpenAPI metadata
│   ├── tests/                         # Pytest test suite (32 unit & integration tests)
│   └── requirements.txt               # Backend dependencies
├── frontend/                          # Single Page Application (React 19 + Vite)
│   ├── src/
│   │   ├── api/client.js              # Dedicated API client talking exclusively to /api/v1
│   │   ├── components/                # Navbar, ProtectedRoute, Modals
│   │   ├── context/                   # AuthContext with token persistence
│   │   ├── pages/                     # 7 Operational Clinic Management Pages
│   │   │   ├── Login.jsx              # Authentication form with quick demo logins
│   │   │   ├── Dashboard.jsx          # Live operational metrics & quick links
│   │   │   ├── Patients.jsx           # Patient directory, substring search & modal
│   │   │   ├── Doctors.jsx            # Specialist directory & weekly schedule slots
│   │   │   ├── BookAppointment.jsx    # Conflict-checked appointment booking wizard
│   │   │   ├── Billing.jsx            # Invoice checkout with discounts & gateways
│   │   │   └── Reports.jsx            # Operations & revenue analytics tabs
│   │   ├── App.jsx                    # React Router configuration
│   │   └── App.css                    # Professional responsive UI styles
│   ├── package.json
│   └── vite.config.js
├── e2e/                               # End-to-End Automation (Headless Chrome Selenium)
│   ├── conftest.py                    # Standardized webdriver fixture & flags
│   ├── test_login_flow.py             # Auth flow validation (failure & success redirect)
│   ├── test_booking_flow.py           # Booking flow & double-booking conflict detection
│   └── runner.py                      # Automated test runner with process lifecycle handling
├── docs/                              # Software Engineering Process Documentation
│   ├── requirements.md                # FRs, NFRs, and 12 user stories with acceptance criteria
│   ├── process-model.md               # Agile Scrum-Lite process model justification
│   ├── patterns.md                    # Design pattern analysis (problems solved & alternatives)
│   ├── uml.md                         # Mermaid UML class diagram of domain & patterns
│   ├── mockup.md                      # ASCII wireframes for all 7 user interfaces
│   ├── new-tool.md                    # Customized Swagger / OpenAPI tool study
│   ├── coverage-summary.md            # Statement coverage metrics (90.0% achieved)
│   ├── test-report.md                 # Detailed test execution & mocking report
│   └── merge-conflict-note.md         # Genuine Git merge conflict simulation & resolution
└── README.md
```

---

## 2. Implemented Design Patterns

The codebase strictly adheres to three classic Gang of Four (GoF) design patterns spanning two distinct categories:

1. **Repository Pattern (Structural / Architectural Data Access Layer)**:
   - *Problem Solved*: Decouples database query mechanics and SQLAlchemy ORM plumbing from route handlers and business services.
   - *Implementation*: `BaseRepository[T]` defines standard generic CRUD operations (`get_by_id`, `get_all`, `create`, `update`, `delete`), extended by concrete repositories (`UserRepository`, `PatientRepository`, `DoctorRepository`, `AppointmentRepository`, `BillingRepository`).
   - *Documentation*: See [docs/patterns.md](docs/patterns.md#3-repository-pattern-architectural--structural-data-access) and [docs/uml.md](docs/uml.md).

2. **Strategy Pattern (Behavioral Calculation Layer)**:
   - *Problem Solved*: Enables interchangeable, open-ended calculation of healthcare discounts and billing calculations without messy conditional logic.
   - *Implementation*: `IDiscountStrategy` interface implemented by `NoDiscountStrategy` (0%), `StudentDiscountStrategy` (18%), `SeniorCitizenDiscountStrategy` (15%), and `InsuranceDiscountStrategy` (80%), coordinated by `BillingCalculationEngine`.
   - *Documentation*: See [docs/patterns.md](docs/patterns.md#2-strategy-pattern-behavioral).

3. **Factory Method Pattern (Creational Payment & Reporting Layer)**:
   - *Problem Solved*: Encapsulates the instantiation of divergent payment channel processors and analytical reporting engines.
   - *Implementation*: 
     - `PaymentProcessorFactory`: Returns `CashPaymentProcessor`, `CardPaymentProcessor`, or `MobileBankingPaymentProcessor`.
     - `ReportGeneratorFactory`: Returns `DailyAppointmentReportGenerator` or `RevenueReportGenerator`.
   - *Documentation*: See [docs/patterns.md](docs/patterns.md#1-factory-pattern-creational).

---

## 3. Technology Stack

- **Backend**: Python 3.11 / 3.13, FastAPI 0.115+, SQLite with SQLAlchemy 2.0 ORM, Pydantic v2 data validation, passlib (bcrypt), python-jose (JWT).
- **Frontend**: React 19, Vite 8, React Router 7, Native Fetch API, responsive CSS3.
- **Testing**: `pytest 9.2`, `pytest-cov 7.1`, `pytest-mock 3.17`, `httpx` ASGI test client, Selenium 4.x (Headless Google Chrome).
- **DevOps & CI**: GitHub Actions multi-runtime pipeline on Ubuntu Linux (`.github/workflows/ci.yml`).

---

## 4. Getting Started & Local Setup

### Prerequisites
- Python 3.11+
- Node.js LTS (v20+) & npm
- Google Chrome browser (for local Selenium E2E runs)

### 4.1 Backend Setup
```bash
# 1. Clone repository
git clone https://github.com/Sifat2128/clinic-appointment-system.git
cd clinic-appointment-system

# 2. Create and activate Python virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r backend/requirements.txt

# 4. Start the backend development server
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```
The backend starts at `http://localhost:8000`. Initial database tables and demo seed records are provisioned automatically on launch.

### 4.2 Frontend Setup
```bash
# In a new terminal window:
cd frontend

# Install node dependencies
npm install

# Start Vite development server
npm run dev
```
The React frontend starts at `http://localhost:5173`.

---

## 5. Seed Accounts & Credentials

The system initializes with ready-to-use demo accounts for immediate grading, review, and automated E2E tests:

| Role | Email | Password | Access Privileges |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin@clinic.com` | `Admin123!` | Full administrative control, staff user creation, doctor profiles |
| **Receptionist** | `receptionist@clinic.com` | `Reception123!` | Patient registration, appointment booking, invoice checkout |
| **Doctor** | `dr.sarah@clinic.com` | `Doctor123!` | Clinical schedules, assigned appointments, patient consultation records |

---

## 6. Testing & Quality Verification

### 6.1 Backend Unit & Integration Tests (TDD)
Execute the complete 32-test backend suite:
```bash
pytest backend/tests -v
```

Execute tests with comprehensive statement coverage:
```bash
pytest --cov=backend.app --cov-report=term-missing backend/tests
```
> **Coverage Metric**: 90.0% code statement coverage achieved (surpasses university requirement of $\ge 80\%$). Detailed breakdown available in [docs/coverage-summary.md](docs/coverage-summary.md).

### 6.2 End-to-End Selenium Tests (Headless Chrome)
The project includes an automated E2E runner that starts both backend and frontend servers, executes the headless Chrome suite, and gracefully tears down processes:
```bash
# From repository root (with virtual environment active):
python e2e/runner.py
```
Verified E2E test cases:
1. `test_login_flow_invalid_credentials`: Submits invalid credentials, verifies error banner, and asserts no unauthorized redirect.
2. `test_login_flow_success`: Submits valid receptionist credentials, verifies JWT receipt, localStorage storage, and dashboard redirection.
3. `test_appointment_booking_and_conflict_prevention_flow`: Books an appointment with doctor/patient pickers and slot selection (201 Created), then re-submits the identical slot to verify real-time double-booking prevention (409 Conflict).

---

## 7. Interactive API Documentation

Interactive API specifications with rich tag categorization, request/response examples, and error schemas are exposed directly by the running backend:
- **Swagger UI Console**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Redoc Visualizer**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Raw OpenAPI 3.0 JSON Contract**: [http://localhost:8000/api/v1/openapi.json](http://localhost:8000/api/v1/openapi.json)

For detailed analysis comparing Swagger to Postman and Redoc, see [docs/new-tool.md](docs/new-tool.md).

---

## 8. Git Discipline & Sessional Requirements

This repository demonstrates rigorous software engineering version control practices:
- **No Direct Commits to `main`**: All features developed on isolated branches (`feature/*`, `bugfix/*`, `docs/*`, `chore/*`) and integrated via GitHub Pull Requests (`gh pr create` / `gh pr merge`).
- **Conventional Commits**: Every commit follows the Conventional Commits specification (`feat:`, `fix:`, `test:`, `docs:`, `chore:`).
- **Strict TDD Evidence**: Features exhibit alternating commits (`test: add failing test for X` followed by `feat: implement X`).
- **Required Git Scenarios**:
  1. *Closed PR*: PR #8 closed without merging with documented institutional compliance rationale.
  2. *Revised PR*: PR #9 reviewed with change requests via `gh pr review`, updated with audit timestamps, and merged.
  3. *Merge Conflict Resolution*: PR #10 and PR #11 simulated a simultaneous modification conflict in `discount_strategy.py`, resolved with full diff history recorded in [docs/merge-conflict-note.md](docs/merge-conflict-note.md).
- **Release Tags**:
  - `v0.1.0`: Sprint 1 completion (Architecture, Requirements, UML, Mockups, Scaffolding, Auth, Patients, Doctors).
  - `v0.2.0`: Sprint 2 completion (Appointments, Conflict Detection, Billing, Reports, Patterns, Swagger docs, Conflict Note).
  - `v1.0.0`: Sprint 3 completion (React Frontend, Selenium E2E Suite, CI Workflow, Root README).

---

## 9. License & Author
- **Author**: Sifat Ahasan `<sifatahasan2108@gmail.com>`
- **Course**: Software Engineering Sessional
- **License**: [MIT License](LICENSE)
