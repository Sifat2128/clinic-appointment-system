import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { appointmentsApi, patientsApi, doctorsApi, billingApi } from '../api/client';

export default function Dashboard() {
  const [stats, setStats] = useState({
    appointmentsCount: 0,
    patientsCount: 0,
    doctorsCount: 0,
    pendingInvoicesCount: 0,
  });
  const [recentAppointments, setRecentAppointments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchDashboardData() {
      try {
        const [appointments, patients, doctors, invoices] = await Promise.all([
          appointmentsApi.getAll().catch(() => []),
          patientsApi.getAll().catch(() => []),
          doctorsApi.getAll().catch(() => []),
          billingApi.getInvoices().catch(() => []),
        ]);

        setStats({
          appointmentsCount: appointments.length,
          patientsCount: patients.length,
          doctorsCount: doctors.length,
          pendingInvoicesCount: invoices.filter((inv) => inv.status === 'PENDING').length,
        });

        // Show latest 5 appointments
        setRecentAppointments(appointments.slice(0, 5));
      } catch (err) {
        console.error('Failed to load dashboard metrics:', err);
      } finally {
        setLoading(false);
      }
    }

    fetchDashboardData();
  }, []);

  return (
    <div className="page-container" data-testid="dashboard-page">
      <div className="page-header">
        <div>
          <h1>Clinic Dashboard</h1>
          <p className="page-subtitle">Overview of operations, bookings, and clinic traffic</p>
        </div>
        <div className="header-actions">
          <Link to="/book-appointment" className="btn btn-primary" data-testid="quick-book-btn">
            + Book Appointment
          </Link>
        </div>
      </div>

      {loading ? (
        <div className="loading-state">Loading dashboard overview...</div>
      ) : (
        <>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon blue">📅</div>
              <div className="stat-content">
                <span className="stat-value" data-testid="stat-appointments-count">{stats.appointmentsCount}</span>
                <span className="stat-label">Total Appointments</span>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon green">👥</div>
              <div className="stat-content">
                <span className="stat-value" data-testid="stat-patients-count">{stats.patientsCount}</span>
                <span className="stat-label">Registered Patients</span>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon purple">🩺</div>
              <div className="stat-content">
                <span className="stat-value" data-testid="stat-doctors-count">{stats.doctorsCount}</span>
                <span className="stat-label">Medical Specialists</span>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon orange">💳</div>
              <div className="stat-content">
                <span className="stat-value" data-testid="stat-pending-invoices">{stats.pendingInvoicesCount}</span>
                <span className="stat-label">Pending Invoices</span>
              </div>
            </div>
          </div>

          <div className="dashboard-content-grid">
            <div className="card">
              <div className="card-header">
                <h3>Recent Appointments</h3>
                <Link to="/reports" className="link-muted">View all reports →</Link>
              </div>
              <div className="card-body">
                {recentAppointments.length === 0 ? (
                  <p className="empty-message">No appointments recorded yet.</p>
                ) : (
                  <table className="data-table" data-testid="dashboard-appointments-table">
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>Patient ID</th>
                        <th>Doctor ID</th>
                        <th>Date & Time</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recentAppointments.map((apt) => (
                        <tr key={apt.id}>
                          <td>#{apt.id}</td>
                          <td>Patient #{apt.patient_id}</td>
                          <td>Doctor #{apt.doctor_id}</td>
                          <td>{new Date(apt.appointment_time).toLocaleString()}</td>
                          <td>
                            <span className={`status-badge status-${apt.status.toLowerCase()}`}>
                              {apt.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <h3>Quick Management</h3>
              </div>
              <div className="card-body quick-actions-list">
                <Link to="/patients" className="quick-action-item">
                  <span className="qa-icon">🧑‍⚕️</span>
                  <div>
                    <strong>Patient Directory</strong>
                    <p>Register new patients or search existing medical profiles</p>
                  </div>
                </Link>

                <Link to="/doctors" className="quick-action-item">
                  <span className="qa-icon">⏱️</span>
                  <div>
                    <strong>Doctor Schedules</strong>
                    <p>Review working hours, slot templates, and availability</p>
                  </div>
                </Link>

                <Link to="/billing" className="quick-action-item">
                  <span className="qa-icon">💵</span>
                  <div>
                    <strong>Invoicing & Checkout</strong>
                    <p>Process invoice payments with discounts and gateways</p>
                  </div>
                </Link>

                <Link to="/reports" className="quick-action-item">
                  <span className="qa-icon">📊</span>
                  <div>
                    <strong>Analytics & Revenue</strong>
                    <p>Export daily appointment metrics and financial reporting</p>
                  </div>
                </Link>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
