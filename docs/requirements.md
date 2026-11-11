# Requirements Specification: Clinic Appointment Management System

## 1. System Overview
The Clinic Appointment Management System is an enterprise healthcare scheduling, patient tracking, billing, and operational reporting platform designed for outpatient clinics. The system streamlines daily clinic operations by connecting three key organizational roles: **Clinic Administrators**, **Doctors**, and **Receptionists/Front-Desk Staff**.

---

## 2. Functional Requirements (FR)

### Module 1: Authentication & Role-Based Access Control (RBAC)
- **FR-1.1**: The system shall authenticate users via email and password using JSON Web Tokens (JWT with HS256 algorithm).
- **FR-1.2**: Passwords shall be securely hashed using standard modern hashing (`bcrypt` / `passlib`) before persistence.
- **FR-1.3**: The system shall enforce role-based access control with three roles: `admin`, `doctor`, and `receptionist`.
- **FR-1.4**: Only administrators shall have privileges to register new staff accounts, modify user roles, or deactivate user accounts.
- **FR-1.5**: Unauthenticated requests to protected endpoints shall return HTTP 401 Unauthorized; unauthorized roles accessing restricted actions shall receive HTTP 403 Forbidden.

### Module 2: Patient Management
- **FR-2.1**: Receptionists and Administrators shall register new patients with mandatory attributes: Full Name, Date of Birth, Gender, Phone Number, and Address.
- **FR-2.2**: The system shall validate phone numbers and ensure uniqueness or duplicate warning alerts.
- **FR-2.3**: Authorized users shall update existing patient demographic information and emergency contact records.
- **FR-2.4**: The system shall provide real-time search functionality by patient name, phone number, or national identification.
- **FR-2.5**: Doctors and receptionists shall append timestamped clinical notes, allergies, and chronic medical history entries to a patient's record.

### Module 3: Doctors & Schedules
- **FR-3.1**: The system shall maintain doctor profiles including full name, specialization (e.g., Cardiology, Dermatology, Pediatrics, General Medicine), contact phone, email, and base consultation fee.
- **FR-3.2**: Doctors and administrators shall configure recurring weekly availability schedule templates (Day of week: Monday–Sunday, Start Time, End Time, Slot Duration in minutes, and Maximum Patient Capacity per slot).
- **FR-3.3**: The system shall dynamically generate bookable consultation time slots based on doctor availability schedules, excluding past times and existing bookings.
- **FR-3.4**: Receptionists and patients shall query active doctors filtered by specialization and date availability.

### Module 4: Appointments Management & Conflict Detection
- **FR-4.1**: Receptionists shall book an appointment linking a registered patient, a doctor, a specific date, and an available time slot.
- **FR-4.2**: **Strict Conflict Detection Engine**:
  - The system shall prevent **Doctor Double-Booking**: A doctor cannot have more than one confirmed appointment in the same time slot on the same date.
  - The system shall prevent **Patient Overlap**: A patient cannot be booked for multiple concurrent appointments with different doctors at the same time.
  - The system shall ensure the selected time falls strictly within the doctor's published working schedule for that day of the week.
- **FR-4.3**: Appointment statuses shall transition through a strict state machine: `SCHEDULED` $\rightarrow$ `COMPLETED` or `CANCELLED`.
- **FR-4.4**: When an appointment is cancelled, the system shall record a mandatory cancellation reason, the cancelling user, and the cancellation timestamp, instantly releasing the time slot.

### Module 5: Billing & Payments
- **FR-5.1**: Upon appointment booking or completion, the system shall generate a unique invoice linking the appointment, patient, and doctor.
- **FR-5.2**: The system shall calculate the gross consultation fee based on doctor specialty rates.
- **FR-5.3**: **Dynamic Discount Strategy**: The system shall apply verified discount policies:
  - *No Discount*: 0% deduction.
  - *Student Discount*: 15% deduction with valid student identification.
  - *Senior Citizen Discount*: 20% deduction for patients aged 60 and above.
  - *Corporate / Insurance Discount*: 30% deduction for covered insurance schemes.
- **FR-5.4**: The system shall compute applicable taxation (5% standard healthcare VAT/tax) on the net discounted subtotal to produce the final payable amount.
- **FR-5.5**: **Payment Processing Factory**: The system shall accept payments via:
  - `CASH`: Direct currency handling with cashier reference.
  - `CARD`: Credit/Debit card processing with simulated authorization gateway.
  - `MOBILE_BANKING`: Electronic wallet (bKash / Nagad / Rocket / M-Pesa) transaction ID verification.
- **FR-5.6**: Invoices shall transition across payment statuses: `PENDING` $\rightarrow$ `PAID` or `REFUNDED`.

### Module 6: Operational Reports & Analytics
- **FR-6.1**: The system shall generate a **Daily Appointment Report** displaying:
  - Total appointments booked for the date.
  - Breakdown by appointment status (`SCHEDULED`, `COMPLETED`, `CANCELLED`).
  - Distribution of patient appointments grouped per doctor and specialization.
- **FR-6.2**: The system shall generate a **Financial Revenue Report** displaying:
  - Gross consultation billing volume.
  - Total discounts granted across all strategies.
  - Total tax collected.
  - Net revenue realized.
  - Breakdown of revenue segregated by payment method (`CASH`, `CARD`, `MOBILE_BANKING`).
- **FR-6.3**: Administrators shall filter reports by specific date ranges and export or render data payloads via standardized REST JSON structures.

---

## 3. Non-Functional Requirements (NFR)

### 3.1 Performance
- **NFR-1.1**: Read queries (patient lookup, doctor schedules, appointment listings) shall execute in less than 150 ms under typical clinic loads.
- **NFR-1.2**: Write transactions (booking appointments, invoice payments) shall complete in less than 300 ms.

### 3.2 Security
- **NFR-2.1**: All sensitive credentials must be hashed using one-way cryptographic algorithms with salt (e.g. `bcrypt`).
- **NFR-2.2**: Authentication tokens (JWT) shall expire after a configurable duration (default: 8 hours) requiring re-authentication.
- **NFR-2.3**: All JSON endpoints must validate input schemas rigorously using Pydantic models to prevent injection and invalid payload structures.

### 3.3 Reliability & Consistency
- **NFR-3.1**: SQLite transactions must operate under ACID guarantees with `WAL` (Write-Ahead Logging) or standard transactional boundaries managed via SQLAlchemy.
- **NFR-3.2**: Database schema constraints (Foreign Keys, Unique Indices on email and time-slot pairs) must be enforced at both the application repository layer and the relational database level.

### 3.4 Maintainability & Extensibility
- **NFR-4.1**: Adherence to SOLID principles:
  - **Single Responsibility Principle (SRP)**: Distinct layers for API routing, business services, and database persistence.
  - **Open/Closed Principle (OCP)**: New payment channels and new reporting formats can be introduced without modifying existing service classes via Factory and Strategy patterns.
- **NFR-4.2**: Decoupled repository layer allowing future switching from SQLite to PostgreSQL without refactoring business service logic.

### 3.5 Testability & Automation
- **NFR-5.1**: Automated test suite shall achieve a minimum of **80% backend code coverage** across all modules.
- **NFR-5.2**: End-to-end user workflows (authentication, appointment booking, conflict validation) shall be verified automatically via headless browser automation (Selenium).

---

## 4. User Stories & Acceptance Criteria

### User Story 1 (US-1): User Authentication & Token Generation
- **As a** clinic employee (Admin, Doctor, Receptionist),
- **I want to** log in with my email and password,
- **So that** I receive a secure access token to perform operations permitted for my role.
- **Acceptance Criteria**:
  - *Given* a registered user with email `"admin@clinic.com"` and password `"Admin@123"`.
  - *When* the user submits valid credentials to `POST /api/v1/auth/login`.
  - *Then* the system returns HTTP 200 with a valid JWT access token, token type `"bearer"`, and user profile data including role.
  - *Given* invalid credentials (incorrect password or unregistered email).
  - *When* credentials are submitted to `POST /api/v1/auth/login`.
  - *Then* the system returns HTTP 401 Unauthorized with an error message `"Invalid email or password"`.

### User Story 2 (US-2): Admin Staff Provisioning
- **As a** Clinic Administrator,
- **I want to** register new staff members and assign their system roles,
- **So that** doctors and receptionists can access the system with appropriate permissions.
- **Acceptance Criteria**:
  - *Given* an authenticated user with role `"admin"`.
  - *When* sending `POST /api/v1/users` with name, unique email, role (`"doctor"` or `"receptionist"`), and password.
  - *Then* the user is persisted in the database and HTTP 201 Created is returned.
  - *Given* an authenticated user with role `"receptionist"` or `"doctor"`.
  - *When* attempting to call `POST /api/v1/users`.
  - *Then* the system rejects the request with HTTP 403 Forbidden.

### User Story 3 (US-3): Patient Registration
- **As a** Receptionist,
- **I want to** register a new patient with their contact and demographic details,
- **So that** they can be scheduled for doctor consultations.
- **Acceptance Criteria**:
  - *Given* a receptionist filling the patient registration form.
  - *When* submitting valid name, DOB, gender, phone number, and address to `POST /api/v1/patients`.
  - *Then* a new patient record is created with a unique ID and HTTP 201 Created is returned.
  - *Given* missing mandatory fields (e.g., missing phone or full name).
  - *When* submitting the payload.
  - *Then* the system returns HTTP 422 Unprocessable Entity specifying missing fields.

### User Story 4 (US-4): Patient Search & Medical Notes
- **As a** Doctor or Receptionist,
- **I want to** search patients by name or phone and view/update medical history notes,
- **So that** patient records are quickly accessible during clinic visits.
- **Acceptance Criteria**:
  - *Given* existing patients in the system.
  - *When* querying `GET /api/v1/patients?search=Rahim`.
  - *Then* all patients whose name or phone matches "Rahim" are returned with HTTP 200.
  - *Given* an existing patient ID.
  - *When* sending `PATCH /api/v1/patients/{id}` with updated allergies and medical history.
  - *Then* the patient record is updated and returned with HTTP 200.

### User Story 5 (US-5): Doctor Profile & Specialty Setup
- **As an** Administrator,
- **I want to** create and maintain doctor profiles with specialization and consultation fees,
- **So that** patients can book appointments with appropriate medical specialists.
- **Acceptance Criteria**:
  - *Given* an admin user.
  - *When* submitting doctor details (user ID, specialization `"Cardiology"`, consultation fee `1000.00`) to `POST /api/v1/doctors`.
  - *Then* the doctor profile is saved and HTTP 201 is returned.

### User Story 6 (US-6): Doctor Schedule Template Configuration
- **As a** Doctor or Administrator,
- **I want to** define weekly schedule slots (day, start time, end time, slot duration, capacity),
- **So that** receptionists can book appointments into valid availability windows.
- **Acceptance Criteria**:
  - *Given* a doctor profile.
  - *When* submitting schedule rules (e.g., `"Monday"`, `"09:00"`, `"12:00"`, slot duration `30` mins, max patients `1`) to `POST /api/v1/doctors/{id}/schedules`.
  - *Then* the schedule is stored and HTTP 201 is returned.
  - *Given* an invalid schedule where end time is before start time (e.g. `"12:00"` to `"09:00"`).
  - *When* submitting the schedule.
  - *Then* the system returns HTTP 400 Bad Request with a validation message.

### User Story 7 (US-7): Appointment Booking with Conflict Prevention
- **As a** Receptionist,
- **I want to** book an appointment for a patient with a selected doctor at a specific slot,
- **So that** consultation sessions are properly organized without scheduling collisions.
- **Acceptance Criteria**:
  - *Given* an available doctor slot on `"2026-11-15"` at `"09:00"`.
  - *When* submitting `POST /api/v1/appointments` with `patient_id`, `doctor_id`, date, and time.
  - *Then* the appointment is created with status `"SCHEDULED"` and HTTP 201 is returned.
  - *Given* an already booked appointment for Doctor A at `"2026-11-15 09:00"`.
  - *When* a second booking is submitted for Doctor A at the same date and time.
  - *Then* the system rejects the booking with HTTP 409 Conflict and message `"Doctor is already booked for this time slot"`.
  - *Given* Patient X is already booked with Doctor A on `"2026-11-15 09:00"`.
  - *When* attempting to book Patient X with Doctor B on `"2026-11-15 09:00"`.
  - *Then* the system rejects with HTTP 409 Conflict and message `"Patient already has a conflicting appointment at this time"`.

### User Story 8 (US-8): Appointment Cancellation
- **As a** Receptionist or Patient,
- **I want to** cancel an existing scheduled appointment with a documented reason,
- **So that** the doctor's time slot is released for other patients.
- **Acceptance Criteria**:
  - *Given* an appointment with status `"SCHEDULED"`.
  - *When* calling `POST /api/v1/appointments/{id}/cancel` with reason `"Patient feeling better"`.
  - *Then* appointment status changes to `"CANCELLED"` and HTTP 200 is returned.
  - *Given* an appointment that is already `"COMPLETED"` or `"CANCELLED"`.
  - *When* attempting to cancel again.
  - *Then* the system returns HTTP 400 Bad Request stating the appointment cannot be cancelled.

### User Story 9 (US-9): Invoice Generation & Discount Calculation
- **As a** Receptionist / Cashier,
- **I want to** generate a bill for an appointment and apply an eligible discount category,
- **So that** patients receive accurate, transparent charges reflecting clinic policies.
- **Acceptance Criteria**:
  - *Given* an appointment with consultation fee `1000.00`.
  - *When* creating an invoice with discount type `"STUDENT"` (15% discount).
  - *Then* the system calculates discount `150.00`, taxable subtotal `850.00`, 5% VAT `42.50`, and total amount payable `892.50`.
  - *Given* discount type `"SENIOR_CITIZEN"` (20% discount).
  - *When* invoice is generated for fee `1000.00`.
  - *Then* discount is `200.00`, taxable subtotal `800.00`, VAT `40.00`, and total payable `840.00`.

### User Story 10 (US-10): Payment Processing via Multiple Channels
- **As a** Cashier,
- **I want to** process payments using Cash, Card, or Mobile Banking,
- **So that** payments are tracked and invoice statuses are updated immediately.
- **Acceptance Criteria**:
  - *Given* a pending invoice of amount `892.50`.
  - *When* submitting `POST /api/v1/billing/{id}/pay` with method `"MOBILE_BANKING"` and transaction reference `"TXN-BKASH-99812"`.
  - *Then* the payment processor records the payment, changes invoice status to `"PAID"`, and returns HTTP 200 with payment receipt.

### User Story 11 (US-11): Daily Appointment Summary Report
- **As a** Clinic Manager or Administrator,
- **I want to** view a daily operational report of all clinic appointments,
- **So that** I can assess clinic capacity, doctor workload, and cancellation rates.
- **Acceptance Criteria**:
  - *Given* appointments recorded on date `"2026-11-15"`.
  - *When* requesting `GET /api/v1/reports/daily-appointments?date=2026-11-15`.
  - *Then* the system returns total appointment count, counts grouped by status (`SCHEDULED`, `COMPLETED`, `CANCELLED`), and list of appointments per doctor.

### User Story 12 (US-12): Revenue Analytics Report
- **As an** Administrator,
- **I want to** view a revenue report for a specified period,
- **So that** I can track clinic earnings, discounts, taxes, and payment method distribution.
- **Acceptance Criteria**:
  - *Given* paid invoices between `"2026-11-01"` and `"2026-11-30"`.
  - *When* requesting `GET /api/v1/reports/revenue?start_date=2026-11-01&end_date=2026-11-30`.
  - *Then* the system returns gross revenue, total discounts given, total tax collected, net revenue collected, and revenue breakdown grouped by payment method (`CASH`, `CARD`, `MOBILE_BANKING`).
