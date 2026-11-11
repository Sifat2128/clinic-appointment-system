# Process Model: Agile (Scrum-Lite)

## 1. Selected Software Process Model
For the **Clinic Appointment Management System** university sessional project, we adopted **Agile (Scrum-Lite)**. This lightweight adaptation of the Scrum framework is tailored for rapid, iterative sessional software engineering projects where high test coverage, strict Git discipline, and progressive feature delivery are evaluated.

---

## 2. Justification for Scrum-Lite

### 2.1 Why Scrum-Lite over Traditional Waterfall?
1. **Iterative Verification & Early Testing**: Waterfall defers testing until after full system implementation. If architectural flaws or data model inconsistencies arise in the appointment conflict or billing logic, discovering them at the end causes severe rework. Scrum-lite enforces strict **Test-Driven Development (TDD)** in each sprint, verifying core business logic from day one.
2. **Incremental Delivery of Working Software**: Graders assess working milestones through tagged releases (`v0.1.0`, `v0.2.0`, `v1.0.0`). In Scrum-lite, each sprint yields a deployable, tested increment rather than an all-or-nothing delivery.
3. **Risk Mitigation**: Building the critical backend foundation (Auth, Patients, Doctors & Schedules) in Sprint 1 allows complex scheduling conflicts, billing strategies, and reporting factories to be tackled in Sprint 2 on a stable bedrock, before assembling the React UI in Sprint 3.

### 2.2 Why Scrum-Lite over Pure Kanban?
1. **Time-Boxed Milestones**: University course deadlines require strict milestone commitments and release tagging. Kanban is continuous flow without predetermined batch milestones, whereas Scrum sprints provide clear time boxes and sprint goals.
2. **Structured Review Ceremonies**: University evaluations benefit from structured sprint reviews and retrospectives where progress, test reports, and pull request histories are documented cleanly.

---

## 3. Sprint Breakdown (3 Sprints)

```mermaid
flowchart LR
    subgraph Sprint 1: Foundations & Core Services
        S1A["Requirements & Architecture Design"] --> S1B["Auth & RBAC Module (TDD)"]
        S1B --> S1C["Patient Management Module (TDD)"]
        S1C --> S1D["Doctor & Schedules Module (TDD)"]
        S1D --> S1E["Sprint 1 Review & Tag v0.1.0"]
    end

    subgraph Sprint 2: Business Logic & Patterns
        S2A["Appointment Booking & Conflict Engine (TDD)"] --> S2B["Billing & Dynamic Discount Strategy (TDD)"]
        S2B --> S2C["Payment Gateway & Report Factory (TDD)"]
        S2C --> S2D["Customized Swagger/OpenAPI Metadata"]
        S2D --> S2E["Conflict Simulation & Tag v0.2.0"]
    end

    subgraph Sprint 3: UI, Automation & Delivery
        S3A["React + Vite Frontend (Components & Pages)"] --> S3B["Selenium E2E Test Suite"]
        S3C["GitHub Actions CI Pipeline"] --> S3D["Final Verification & Tag v1.0.0"]
        S3B --> S3D
        S3A --> S3C
    end

    Sprint 1: Foundations & Core Services --> Sprint 2: Business Logic & Patterns
    Sprint 2: Business Logic & Patterns --> Sprint 3: UI, Automation & Delivery
```

### Sprint 1: Architecture, Core Entities & Foundation
- **Goal**: Establish the repository infrastructure, write comprehensive architecture and design documents, set up the SQLite SQLAlchemy persistence layer, and build the foundational backend modules using strict TDD.
- **Scope & Deliverables**:
  - `docs/requirements.md`, `docs/process-model.md`, `docs/patterns.md`, `docs/uml.md`, `docs/mockup.md`.
  - Backend project scaffolding with FastAPI, SQLite, Pydantic, SQLAlchemy, and pytest.
  - **Module 1**: Authentication & RBAC (Admin, Doctor, Receptionist) with JWT.
  - **Module 2**: Patient management (CRUD, search, medical notes).
  - **Module 3**: Doctors & weekly schedule slots management.
  - Repository Pattern implementation decoupling services from ORM.
  - Pull requests created and merged via GitHub CLI (`gh`).
  - **Milestone Release**: `v0.1.0`.

### Sprint 2: Complex Business Logic, Design Patterns & OpenAPI
- **Goal**: Implement the core domain business rules—appointment conflict checking, billing calculation with Strategy pattern, payment processing with Factory pattern, and reporting factory—backed by isolated unit and mock tests.
- **Scope & Deliverables**:
  - **Module 4**: Appointment booking, state machine transitions, and strict double-booking conflict detection.
  - **Module 5**: Billing & Invoicing, Dynamic Discount Strategy (No Discount, Student, Senior Citizen, Insurance), VAT calculation, Payment Processor Factory (Cash, Card, Mobile Banking).
  - **Module 6**: Reporting Engine (Daily Appointment Report, Revenue Analytics Report).
  - Customized OpenAPI / Swagger documentation (tags, descriptions, examples, error models).
  - Git exercises: Deliberate merge conflict simulation & resolution (`docs/merge-conflict-note.md`), PR revision review, PR closure.
  - Test coverage verification (80%+ target), generating `docs/coverage-summary.md` and `docs/test-report.md`.
  - **Milestone Release**: `v0.2.0`.

### Sprint 3: Frontend Integration, Selenium E2E Automation & CI/CD
- **Goal**: Construct the responsive React (Vite) single-page application, integrate with backend REST endpoints via a typed client, automate browser verification with headless Selenium, and configure the GitHub Actions CI pipeline.
- **Scope & Deliverables**:
  - React SPA with React Router: Login, Dashboard, Patients, Doctors & Schedules, Book Appointment, Billing, Reports.
  - Form validation, dynamic error handling, and `data-testid` attributes on interactive elements.
  - End-to-end Selenium test suite (headless Chrome) testing critical user paths:
    1. Login flow (invalid credentials error display, successful authentication, role-based redirect).
    2. Appointment booking flow (slot selection, patient linking, conflict handling).
  - CI pipeline (`.github/workflows/ci.yml`) configuring Python 3.11 + Node.js, running pytest with coverage, building Vite frontend, and executing headless Selenium E2E tests.
  - Comprehensive `README.md` with CI badge and project execution guide.
  - **Final Milestone Release**: `v1.0.0`.

---

## 4. Scrum Ceremonies in Sessional Context
- **Sprint Planning**: At the onset of each sprint, user stories are selected from `docs/requirements.md`, mapped to Git branches, and given explicit test acceptance criteria.
- **TDD Flow (Red-Green-Refactor)**: Every feature begins with a failing test commit (`test: add failing test for X`), followed by implementation and passing test commit (`feat: implement X`).
- **Sprint Review & Retrospective**: At the end of each sprint, the test suite is executed, coverage metrics are reviewed, Git tags are minted, and artifacts are verified against the sessional grading rubric.
