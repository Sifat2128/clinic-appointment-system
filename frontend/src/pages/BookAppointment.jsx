import React, { useState, useEffect } from 'react';
import { doctorsApi, patientsApi, appointmentsApi } from '../api/client';

export default function BookAppointment() {
  const [doctors, setDoctors] = useState([]);
  const [patients, setPatients] = useState([]);
  const [selectedDoctorId, setSelectedDoctorId] = useState('');
  const [selectedPatientId, setSelectedPatientId] = useState('');
  const [appointmentDate, setAppointmentDate] = useState(() => {
    // Default to tomorrow or next weekday
    const d = new Date();
    d.setDate(d.getDate() + 1);
    return d.toISOString().split('T')[0];
  });
  const [availableSlots, setAvailableSlots] = useState([]);
  const [selectedSlot, setSelectedSlot] = useState('');
  const [reason, setReason] = useState('Routine Checkup');
  const [loadingSlots, setLoadingSlots] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const [conflictError, setConflictError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    async function loadData() {
      try {
        const [docs, pts] = await Promise.all([
          doctorsApi.getAll().catch(() => []),
          patientsApi.getAll().catch(() => []),
        ]);
        setDoctors(docs);
        setPatients(pts);

        if (docs.length > 0) setSelectedDoctorId(String(docs[0].id));
        if (pts.length > 0) setSelectedPatientId(String(pts[0].id));
      } catch (err) {
        console.error('Error loading doctors/patients:', err);
      }
    }
    loadData();
  }, []);

  // Fetch slots whenever selected doctor or appointment date changes
  useEffect(() => {
    async function fetchSlots() {
      if (!selectedDoctorId || !appointmentDate) {
        setAvailableSlots([]);
        return;
      }
      setLoadingSlots(true);
      setConflictError('');
      try {
        const slots = await doctorsApi.getAvailableSlots(selectedDoctorId, appointmentDate);
        setAvailableSlots(slots);
        if (slots.length > 0) {
          setSelectedSlot(slots[0].slot_start);
        } else {
          setSelectedSlot('');
        }
      } catch (err) {
        console.warn('Could not fetch slots:', err);
        setAvailableSlots([]);
      } finally {
        setLoadingSlots(false);
      }
    }

    fetchSlots();
  }, [selectedDoctorId, appointmentDate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setConflictError('');
    setSuccessMessage('');

    if (!selectedPatientId || !selectedDoctorId || !selectedSlot) {
      setConflictError('Please select patient, doctor, date, and an available time slot.');
      return;
    }

    setSubmitting(true);
    try {
      const payload = {
        patient_id: Number(selectedPatientId),
        doctor_id: Number(selectedDoctorId),
        appointment_time: selectedSlot,
        duration_minutes: 30,
        reason_for_visit: reason,
      };

      const result = await appointmentsApi.create(payload);
      setSuccessMessage(
        `Appointment successfully booked! (ID: #${result.id}) Confirmed for ${new Date(result.appointment_time).toLocaleString()}`
      );
      // Refresh available slots
      const slots = await doctorsApi.getAvailableSlots(selectedDoctorId, appointmentDate);
      setAvailableSlots(slots);
      if (slots.length > 0) setSelectedSlot(slots[0].slot_start);
    } catch (err) {
      // 409 Conflict check
      const detail = err.data?.detail || err.message || 'Booking conflict detected';
      setConflictError(detail);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="page-container" data-testid="book-appointment-page">
      <div className="page-header">
        <div>
          <h1>Book Clinical Appointment</h1>
          <p className="page-subtitle">Schedule a consultation with automated conflict detection</p>
        </div>
      </div>

      {conflictError && (
        <div className="alert alert-danger" data-testid="booking-conflict-alert">
          <strong>Booking Conflict:</strong> {conflictError}
        </div>
      )}

      {successMessage && (
        <div className="alert alert-success" data-testid="booking-success-alert">
          <strong>Success!</strong> {successMessage}
        </div>
      )}

      <div className="card max-w-700">
        <div className="card-body">
          <form onSubmit={handleSubmit} className="booking-form">
            <div className="form-group">
              <label htmlFor="select-patient">Select Patient *</label>
              <select
                id="select-patient"
                data-testid="select-patient"
                value={selectedPatientId}
                onChange={(e) => setSelectedPatientId(e.target.value)}
                required
              >
                {patients.length === 0 && <option value="">No patients registered</option>}
                {patients.map((p) => (
                  <option key={p.id} value={p.id}>
                    #{p.id} - {p.first_name} {p.last_name} ({p.phone})
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="select-doctor">Select Specialist Doctor *</label>
              <select
                id="select-doctor"
                data-testid="select-doctor"
                value={selectedDoctorId}
                onChange={(e) => setSelectedDoctorId(e.target.value)}
                required
              >
                {doctors.length === 0 && <option value="">No doctors available</option>}
                {doctors.map((doc) => (
                  <option key={doc.id} value={doc.id}>
                    Dr. {doc.user?.full_name || `Doctor #${doc.id}`} ({doc.specialization} - ${Number(doc.consultation_fee).toFixed(2)})
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="select-date">Appointment Date *</label>
              <input
                id="select-date"
                type="date"
                data-testid="select-date"
                value={appointmentDate}
                onChange={(e) => setAppointmentDate(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="select-slot">
                Available Time Slots * {loadingSlots && <span className="text-muted">(Checking doctor availability...)</span>}
              </label>

              {availableSlots.length > 0 ? (
                <select
                  id="select-slot"
                  data-testid="select-slot"
                  value={selectedSlot}
                  onChange={(e) => setSelectedSlot(e.target.value)}
                  required
                >
                  {availableSlots.map((slot, index) => {
                    const timeStr = new Date(slot.slot_start).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
                    return (
                      <option key={index} value={slot.slot_start} data-testid="slot-option">
                        {timeStr} - Slot {index + 1}
                      </option>
                    );
                  })}
                </select>
              ) : (
                <div className="alert alert-warning">
                  No slots currently available for this doctor on {appointmentDate}. You may enter a custom appointment ISO time or choose another date.
                  <input
                    type="datetime-local"
                    className="custom-slot-input"
                    value={selectedSlot ? selectedSlot.slice(0, 16) : ''}
                    onChange={(e) => setSelectedSlot(new Date(e.target.value).toISOString())}
                    data-testid="custom-slot-input"
                  />
                </div>
              )}
            </div>

            <div className="form-group">
              <label htmlFor="input-reason">Reason for Visit</label>
              <input
                id="input-reason"
                type="text"
                data-testid="input-reason"
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="e.g. Chest pain, Follow-up consultation, Routine checkup"
              />
            </div>

            <div className="form-actions">
              <button
                type="submit"
                className="btn btn-primary btn-block"
                data-testid="confirm-booking-btn"
                disabled={submitting}
              >
                {submitting ? 'Verifying & Booking...' : 'Confirm Appointment'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
