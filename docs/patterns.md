# Software Design Patterns Documentation

In accordance with sessional architecture requirements, this project implements three core design patterns across distinct Gang of Four (GoF) categories: **Creational (Factory Method)**, **Behavioral (Strategy)**, and **Structural (Repository)**.

---

## 1. Factory Pattern (Creational Category)

### 1.1 Use Case A: Payment Method Creation (`PaymentProcessorFactory`)

#### Problem It Solves
A clinic must support diverse payment methods (`CASH`, `CARD`, `MOBILE_BANKING`) which involve different validation rules, external gateway simulations, and receipt generation logic. Embedding payment method instantiation directly inside the billing service creates conditional coupling (`if method == 'cash' ... elif method == 'card' ...`). If a new payment channel (such as Apple Pay or Insurance Direct) is introduced, the billing service code must be modified, directly violating the **Open/Closed Principle (OCP)**.

The `PaymentProcessorFactory` encapsulates the instantiation logic into a central, extensible registry. The billing service requests a processor for a payment method string and executes `.process_payment()` uniformly.

#### Alternative Considered & Rejected
- **Alternative**: Direct Instantiation within the Service layer via `if-elif-else` branches.
- **Reason for Rejection**: Direct instantiation tightly couples the business service to concrete payment processor classes. Whenever new payment channels are added, unit tests for the entire billing service must be re-executed and potentially rewritten. Direct instantiation also makes mocking individual payment processors during unit tests cumbersome.

---

### 1.2 Use Case B: Report Type Creation (`ReportGeneratorFactory`)

#### Problem It Solves
The clinic management requires distinct analytical summaries: **Daily Appointments Report** and **Financial Revenue Report**. Each report pulls from different database tables, aggregates data using distinct algorithms, and returns different schema structures. Consolidating report generation into a single monolithic report class leads to bloated methods with low cohesion.

`ReportGeneratorFactory` provides a common interface (`IReportGenerator`) and dynamically instantiates the correct generator based on the requested report type (`daily_appointments`, `revenue`).

#### Alternative Considered & Rejected
- **Alternative**: Abstract Factory Pattern.
- **Reason for Rejection**: Abstract Factory creates *families* of related or dependent objects (e.g., Mac vs. Windows UI kits). Here, we only need to instantiate a single product type (a specific report generator). Introducing Abstract Factory would add redundant interface abstractions, extra classes, and unnecessary architectural complexity without any practical gain.

---

## 2. Strategy Pattern (Behavioral Category)

### 2.1 Use Case: Discount & Payment Calculation (`DiscountStrategy`)

#### Problem It Solves
Clinic billing applies different discount rules depending on the patient's category:
- **Regular Patient**: 0% discount (`NoDiscountStrategy`).
- **Student**: 15% discount on consultation fees (`StudentDiscountStrategy`).
- **Senior Citizen (Age 60+)**: 20% discount (`SeniorCitizenDiscountStrategy`).
- **Insurance / Corporate Member**: 30% discount (`InsuranceDiscountStrategy`).

Hardcoding these formulas inside the billing calculation leads to brittle code where changes to discount rates or eligibility rules risk introducing bugs into the general invoice calculation pipeline. 

The **Strategy Pattern** defines a family of discount algorithms, encapsulates each one into its own class conforming to `IDiscountStrategy`, and makes them interchangeable at runtime. The `BillingCalculationEngine` delegates calculation to the injected strategy:
$$\text{Discount Amount} = \text{Strategy}.\text{calculate\_discount}(\text{Base Fee})$$
$$\text{Taxable Subtotal} = \text{Base Fee} - \text{Discount Amount}$$
$$\text{Tax (5\%)} = \text{Taxable Subtotal} \times 0.05$$
$$\text{Total Payable} = \text{Taxable Subtotal} + \text{Tax}$$

#### Alternative Considered & Rejected
- **Alternative**: Decorator Pattern for stacking discounts.
- **Reason for Rejection**: The clinic's business policy enforces that discount schemes are strictly *mutually exclusive* (a patient cannot stack a Senior Citizen discount on top of a Student discount). The Decorator pattern is designed to dynamically wrap and chain multiple behaviors together. Using Decorator here would overcomplicate the logic and make preventing illegitimate discount stacking error-prone compared to a single, clean Strategy.

---

## 3. Repository Pattern (Structural / Architectural Category)

### 3.1 Use Case: Database Access & Persistence Layer (`BaseRepository`)

#### Problem It Solves
Modern web applications often tightly couple ORM queries (`db.query(UserModel).filter(...).all()`) directly inside HTTP request handlers or business services. This tight coupling makes it nearly impossible to write fast, isolated unit tests without spinning up a live relational database instance. It also leaks database-specific details (SQLAlchemy session lifecycle, query syntax) into business logic.

The **Repository Pattern** abstracts data persistence behind a collection-like interface:
- `UserRepository`
- `PatientRepository`
- `DoctorRepository`
- `AppointmentRepository`
- `BillingRepository`
- `ReportRepository`

Each repository implements standard CRUD operations (`get_by_id`, `get_all`, `create`, `update`, `delete`) as well as domain-specific queries (`find_by_email`, `check_appointment_conflict`, `get_appointments_by_date`). Business services depend only on these repository interfaces.

#### Alternative Considered & Rejected
- **Alternative**: Active Record Pattern (models containing both schema definition and persistence methods like `patient.save()`, `patient.delete()`).
- **Reason for Rejection**: Active Record violates the **Single Responsibility Principle (SRP)** by conflating data modeling with SQL persistence logic. In testing, Active Record models cannot be easily mocked without mocking low-level database drivers, severely hindering TDD speed and coverage verification.

---

## 4. Pattern Summary Matrix

| Pattern | Category | Project Component | Key Benefit |
| :--- | :--- | :--- | :--- |
| **Factory Method** | Creational | `PaymentProcessorFactory`, `ReportGeneratorFactory` | Open/Closed Principle: easily add new payment gateways or report types without touching existing services. |
| **Strategy** | Behavioral | `DiscountStrategy` (`NoDiscount`, `Student`, `SeniorCitizen`, `Insurance`) | Runtime algorithm swapping; clean mathematical separation of promotional and healthcare discount rules. |
| **Repository** | Structural | `BaseRepository`, `AppointmentRepository`, `BillingRepository`, etc. | Decouples business logic from SQLAlchemy/SQLite; facilitates pure unit testing and mock-based TDD. |
