import React, { useState, useEffect } from 'react';
import { doctorsApi } from '../api/client';

const DAYS = ['MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY'];

export default function Doctors() {
  const [doctors, setDoctors] = useState([]);
  const [selectedDoctor, setSelectedDoctor] = useState(null);
  const [schedules, setSchedules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showScheduleModal, setShowScheduleModal] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [scheduleForm, setScheduleForm] = useState({
    day_of_week: 'MONDAY',
    start_time: '09:00:00',
    end_time: '13:00:00',
    slot_duration_minutes: 30,
    is_active: true,
  });

  const fetchDoctors = async () => {
    try {
      setLoading(true);
      const data = await doctorsApi.getAll();
      setDoctors(data);
      if (data.length > 0 && !selectedDoctor) {
        handleSelectDoctor(data[0]);
      }
    } catch (err) {
      setError('Failed to fetch doctors list');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectDoctor = async (doctor) => {
    setSelectedDoctor(doctor);
    try {
      const sched = await doctorsApi.getSchedules(doctor.id);
      setSchedules(sched);
    } catch (err) {
      setSchedules([]);
    }
  };

  useEffect(() => {
    fetchDoctors();
  }, []);

  const handleAddSchedule = async (e) => {
    e.preventDefault();
    if (!selectedDoctor) return;
    setError('');
    setSuccess('');

    try {
      await doctorsApi.createSchedule(selectedDoctor.id, scheduleForm);
      setSuccess(`Schedule template added for Dr. ${selectedDoctor.user?.full_name || selectedDoctor.specialization}!`);
      setShowScheduleModal(false);
      handleSelectDoctor(selectedDoctor);
    } catch (err) {
      setError(err.message || 'Failed to create schedule');
    }
  };

  return (
    <div className="page-container" data-testid="doctors-page">
      <div className="page-header">
        <div>
          <h1>Specialists & Working Schedules</h1>
          <p className="page-subtitle">Manage doctor clinical availability and appointment slot generators</p>
        </div>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}

      <div className="two-column-layout">
        <div className="card">
          <div className="card-header">
            <h3>Registered Specialists</h3>
          </div>
          <div className="card-body">
            {loading ? (
              <div className="loading-state">Loading doctors...</div>
            ) : (
              <div className="doctor-list" data-testid="doctors-list">
                {doctors.map((doc) => (
                  <div
                    key={doc.id}
                    onClick={() => handleSelectDoctor(doc)}
                    className={`doctor-card-item ${selectedDoctor?.id === doc.id ? 'active' : ''}`}
                    data-testid={`doctor-item-${doc.id}`}
                  >
                    <div className="doc-avatar">🩺</div>
                    <div className="doc-details">
                      <h4>Dr. {doc.user?.full_name || `Doctor #${doc.id}`}</h4>
                      <p className="doc-spec">{doc.specialization} • {doc.department}</p>
                      <p className="doc-meta">
                        Fee: <strong>${Number(doc.consultation_fee).toFixed(2)}</strong> | Room {doc.room_number || '101'}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="card">
          <div className="card-header flex-between">
            <h3>
              {selectedDoctor
                ? `Schedule: Dr. ${selectedDoctor.user?.full_name || selectedDoctor.specialization}`
                : 'Doctor Schedule'}
            </h3>
            {selectedDoctor && (
              <button
                className="btn btn-primary btn-sm"
                onClick={() => setShowScheduleModal(true)}
                data-testid="add-schedule-btn"
              >
                + Add Weekly Schedule
              </button>
            )}
          </div>
          <div className="card-body">
            {!selectedDoctor ? (
              <p className="empty-message">Select a doctor on the left to inspect schedules.</p>
            ) : schedules.length === 0 ? (
              <div className="empty-state">
                <p>No active weekly availability schedules found for this doctor.</p>
                <button
                  className="btn btn-outline btn-sm"
                  onClick={() => setShowScheduleModal(true)}
                >
                  Configure Working Hours
                </button>
              </div>
            ) : (
              <table className="data-table" data-testid="schedules-table">
                <thead>
                  <tr>
                    <th>Day</th>
                    <th>Hours</th>
                    <th>Slot Duration</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {schedules.map((s) => (
                    <tr key={s.id}>
                      <td><strong>{s.day_of_week}</strong></td>
                      <td>{s.start_time.slice(0, 5)} - {s.end_time.slice(0, 5)}</td>
                      <td>{s.slot_duration_minutes} mins</td>
                      <td>
                        <span className="status-badge status-scheduled">
                          {s.is_active ? 'ACTIVE' : 'INACTIVE'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>

      {showScheduleModal && (
        <div className="modal-backdrop">
          <div className="modal-dialog">
            <div className="modal-header">
              <h3>Add Weekly Schedule Template</h3>
              <button className="btn-close" onClick={() => setShowScheduleModal(false)}>×</button>
            </div>
            <form onSubmit={handleAddSchedule}>
              <div className="modal-body form-grid">
                <div className="form-group">
                  <label>Day of Week *</label>
                  <select
                    value={scheduleForm.day_of_week}
                    onChange={(e) => setScheduleForm({ ...scheduleForm, day_of_week: e.target.value })}
                  >
                    {DAYS.map((d) => (
                      <option key={d} value={d}>{d}</option>
                    ))}
                  </select>
                </div>
                <div className="form-group">
                  <label>Slot Duration (minutes) *</label>
                  <select
                    value={scheduleForm.slot_duration_minutes}
                    onChange={(e) => setScheduleForm({ ...scheduleForm, slot_duration_minutes: Number(e.target.value) })}
                  >
                    <option value={15}>15 minutes</option>
                    <option value={20}>20 minutes</option>
                    <option value={30}>30 minutes</option>
                    <option value={45}>45 minutes</option>
                    <option value={60}>60 minutes</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Start Time (HH:MM:SS) *</label>
                  <input
                    type="text"
                    required
                    value={scheduleForm.start_time}
                    onChange={(e) => setScheduleForm({ ...scheduleForm, start_time: e.target.value })}
                    placeholder="09:00:00"
                  />
                </div>
                <div className="form-group">
                  <label>End Time (HH:MM:SS) *</label>
                  <input
                    type="text"
                    required
                    value={scheduleForm.end_time}
                    onChange={(e) => setScheduleForm({ ...scheduleForm, end_time: e.target.value })}
                    placeholder="13:00:00"
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-outline" onClick={() => setShowScheduleModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" data-testid="save-schedule-btn">
                  Save Schedule
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
