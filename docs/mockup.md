# UI Wireframes & Mockups: Clinic Appointment Management System

This document outlines the user interface wireframes and layout structures for the React single-page frontend.

---

## 1. Login Page (`/login`)

```text
+-----------------------------------------------------------------------+
|                       CLINIC APPOINTMENT SYSTEM                       |
+-----------------------------------------------------------------------+
|                                                                       |
|                     +-----------------------------+                   |
|                     |        Staff Login          |                   |
|                     +-----------------------------+                   |
|                     | Email:                      |                   |
|                     | [ user@clinic.com         ] | (data-testid=email)
|                     | Password:                   |                   |
|                     | [ *******************     ] | (data-testid=pass)|
|                     |                             |                   |
|                     | [     Sign In Button      ] | (data-testid=btn) |
|                     |                             |                   |
|                     | [ Alert: Error message area ] |                 |
|                     +-----------------------------+                   |
|                                                                       |
+-----------------------------------------------------------------------+
```

---

## 2. Main Layout & Dashboard (`/dashboard`)

```text
+-----------------------------------------------------------------------+
|  CLINIC AMS LOGO  | Dashboard | Patients | Doctors | Book | Billing | Reports | User (Admin) [Logout] |
+-----------------------------------------------------------------------+
|  Welcome back, Dr. Rahim / Receptionist Sarah!                        |
|                                                                       |
|  +--------------------+  +--------------------+  +------------------+ |
|  | Today's Appts      |  | Active Doctors     |  | Total Revenue    | |
|  |     24 Patients    |  |     8 On Duty      |  |    $12,450.00    | |
|  +--------------------+  +--------------------+  +------------------+ |
|                                                                       |
|  Upcoming Appointments Today:                                         |
|  +----+--------------+-------------------+----------+---------------+ |
|  | ID | Patient Name | Doctor            | Time     | Status        | |
|  +----+--------------+-------------------+----------+---------------+ |
|  | 101| Alice Smith  | Dr. Rahim (Cardio)| 09:30 AM | SCHEDULED     | |
|  | 102| Bob Johnson  | Dr. Maria (Pedia) | 10:00 AM | COMPLETED     | |
|  +----+--------------+-------------------+----------+---------------+ |
+-----------------------------------------------------------------------+
```

---

## 3. Patients Management Page (`/patients`)

```text
+-----------------------------------------------------------------------+
|  PATIENT MANAGEMENT                                                   |
|  Search: [ Rahim               ] [ + Register New Patient Button ]    |
|  (data-testid="patient-search")    (data-testid="btn-add-patient")    |
+-----------------------------------------------------------------------+
|  Patient Directory:                                                   |
|  +----+------------------+-------------+--------------+-------------+ |
|  | ID | Full Name        | Phone       | Gender / Age | Actions     | |
|  +----+------------------+-------------+--------------+-------------+ |
|  | 1  | Tanvir Ahmed     | +8801711... | Male, 34     | [Edit][View]| |
|  | 2  | Fatima Begum     | +8801912... | Female, 62   | [Edit][View]| |
|  +----+------------------+-------------+--------------+-------------+ |
|                                                                       |
|  [ MODAL / FORM: Register Patient ]                                   |
|  - Full Name: [                     ] (data-testid="patient-name")    |
|  - DOB:       [ YYYY-MM-DD          ] (data-testid="patient-dob")     |
|  - Gender:    [ Male/Female/Other v ] (data-testid="patient-gender")  |
|  - Phone:     [ 017xxxxxxxx         ] (data-testid="patient-phone")   |
|  - Address:   [ Street, City        ] (data-testid="patient-address") |
|  - Allergies: [ Penicillin, Dust    ]                                 |
|  [ Cancel ]                 [ Save Patient (data-testid="btn-save") ] |
+-----------------------------------------------------------------------+
```

---

## 4. Doctors & Schedules Page (`/doctors`)

```text
+-----------------------------------------------------------------------+
|  DOCTORS & WEEKLY SCHEDULES                                           |
|  [ + Add Doctor Profile ]  [ + Configure Schedule Slot ]              |
+-----------------------------------------------------------------------+
|  Doctor Directory:                                                    |
|  +-----------------------------------------------------------------+  |
|  | Dr. Tanvir Rahman - Cardiology (Fee: $1,200)                    |  |
|  | Phone: 01812345678 | Email: doc.tanvir@clinic.com               |  |
|  | Weekly Availability:                                            |  |
|  |   - Monday:    09:00 - 13:00 (Slot: 30m, Max: 1/slot)           |  |
|  |   - Wednesday: 14:00 - 18:00 (Slot: 30m, Max: 1/slot)           |  |
|  +-----------------------------------------------------------------+  |
|  | Dr. Nusrat Jahan - Pediatrics (Fee: $1,000)                     |  |
|  | Weekly Availability:                                            |  |
|  |   - Tuesday:   10:00 - 14:00 (Slot: 30m, Max: 1/slot)           |  |
|  |   - Thursday:  10:00 - 14:00 (Slot: 30m, Max: 1/slot)           |  |
|  +-----------------------------------------------------------------+  |
+-----------------------------------------------------------------------+
```

---

## 5. Book Appointment Page (`/book-appointment`)

```text
+-----------------------------------------------------------------------+
|  BOOK APPOINTMENT                                                     |
+-----------------------------------------------------------------------+
|  Step 1: Select Patient:                                              |
|  [ Select Patient from list...   v ] (data-testid="select-patient")   |
|                                                                       |
|  Step 2: Select Doctor & Date:                                        |
|  Doctor: [ Dr. Tanvir Rahman (Cardio) v ] (data-testid="select-doc")  |
|  Date:   [ 2026-11-15                 ] (data-testid="select-date") |
|                                                                       |
|  Step 3: Available Time Slots:                                        |
|  ( ) 09:00 AM   (*) 09:30 AM   ( ) 10:00 AM   (X) 10:30 AM (Booked)   |
|  (data-testid="slot-radio")                                           |
|                                                                       |
|  Consultation Reason:                                                 |
|  [ Routine heart checkup and blood pressure reading                ]  |
|                                                                       |
|  [!] Conflict Warning Banner (appears dynamically if slot taken)      |
|                                                                       |
|  [ Confirm Booking (data-testid="btn-confirm-booking") ]              |
+-----------------------------------------------------------------------+
```

---

## 6. Billing & Invoice Page (`/billing`)

```text
+-----------------------------------------------------------------------+
|  BILLING & PAYMENT CHECKOUT                                           |
+-----------------------------------------------------------------------+
|  Invoice #INV-2026-0042                                               |
|  Patient: Tanvir Ahmed | Doctor: Dr. Tanvir Rahman                    |
|  Consultation Base Fee:                                    $1,200.00  |
|                                                                       |
|  Select Discount Strategy:                                            |
|  (*) Student (15%)   ( ) Senior Citizen (20%)   ( ) Insurance (30%)   |
|  Discount Applied (-15%):                                  - $180.00  |
|  Taxable Subtotal:                                         $1,020.00  |
|  Standard Healthcare VAT (5%):                               +$51.00  |
|  -------------------------------------------------------------------  |
|  TOTAL PAYABLE:                                            $1,071.00  |
|                                                                       |
|  Select Payment Channel:                                              |
|  [ ] Cash         [*] Card         [ ] Mobile Banking (bKash/Nagad)   |
|  Transaction Reference: [ TXN-CARD-982312            ]                |
|                                                                       |
|  [ Process Payment (data-testid="btn-pay") ]  [ Print Receipt ]       |
+-----------------------------------------------------------------------+
```

---

## 7. Reports & Analytics Page (`/reports`)

```text
+-----------------------------------------------------------------------+
|  OPERATIONAL & FINANCIAL REPORTS                                      |
|  Report Type: [ Daily Appointments Report v ]  Date: [ 2026-11-15 ]   |
|  [ Generate Report Button (data-testid="btn-generate-report") ]       |
+-----------------------------------------------------------------------+
|  REPORT SUMMARY:                                                      |
|  - Total Appointments: 18                                             |
|  - Status Breakdown: 14 Completed, 3 Scheduled, 1 Cancelled           |
|                                                                       |
|  Doctor Workload Distribution:                                        |
|  - Dr. Tanvir (Cardiology):  8 Appointments                           |
|  - Dr. Nusrat (Pediatrics):  6 Appointments                           |
|  - Dr. Maria (General):      4 Appointments                           |
|                                                                       |
|  Revenue Breakdown (Financial View):                                  |
|  - Gross Billed:     $18,000.00                                       |
|  - Total Discounts:   $2,700.00                                       |
|  - VAT Collected:       $765.00                                       |
|  - Net Received:     $16,065.00 (Cash: $5,000 | Card: $8k | Mobile: $3k)|
+-----------------------------------------------------------------------+
```
