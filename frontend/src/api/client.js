/**
 * Clinic Appointment Management System
 * API Client Module
 * Communicates exclusively with FastAPI backend under /api/v1
 */

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000/api/v1';

async function request(endpoint, options = {}) {
  const token = localStorage.getItem('token');
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 204) {
    return null;
  }

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const error = new Error(data?.detail || data?.message || 'API request failed');
    error.status = response.status;
    error.data = data;
    throw error;
  }

  return data;
}

export const authApi = {
  login: (email, password) =>
    request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),
  register: (userData) =>
    request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    }),
  getMe: () => request('/auth/me'),
};

export const patientsApi = {
  getAll: (search = '') =>
    request(`/patients${search ? `?search=${encodeURIComponent(search)}` : ''}`),
  getById: (id) => request(`/patients/${id}`),
  create: (patientData) =>
    request('/patients', {
      method: 'POST',
      body: JSON.stringify(patientData),
    }),
  update: (id, patientData) =>
    request(`/patients/${id}`, {
      method: 'PUT',
      body: JSON.stringify(patientData),
    }),
  delete: (id) =>
    request(`/patients/${id}`, {
      method: 'DELETE',
    }),
};

export const doctorsApi = {
  getAll: () => request('/doctors'),
  getById: (id) => request(`/doctors/${id}`),
  create: (doctorData) =>
    request('/doctors', {
      method: 'POST',
      body: JSON.stringify(doctorData),
    }),
  getSchedules: (doctorId) => request(`/doctors/${doctorId}/schedules`),
  createSchedule: (doctorId, scheduleData) =>
    request(`/doctors/${doctorId}/schedules`, {
      method: 'POST',
      body: JSON.stringify(scheduleData),
    }),
  getAvailableSlots: (doctorId, date) =>
    request(`/doctors/${doctorId}/available-slots?date=${date}`),
};

export const appointmentsApi = {
  getAll: (status = '', date = '') => {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (date) params.append('date', date);
    const query = params.toString() ? `?${params.toString()}` : '';
    return request(`/appointments${query}`);
  },
  getById: (id) => request(`/appointments/${id}`),
  create: (appointmentData) =>
    request('/appointments', {
      method: 'POST',
      body: JSON.stringify(appointmentData),
    }),
  updateStatus: (id, statusData) =>
    request(`/appointments/${id}/status`, {
      method: 'PATCH',
      body: JSON.stringify(statusData),
    }),
};

export const billingApi = {
  getInvoices: () => request('/billing/invoices'),
  getInvoice: (id) => request(`/billing/invoices/${id}`),
  payInvoice: (id, paymentData) =>
    request(`/billing/invoices/${id}/pay`, {
      method: 'POST',
      body: JSON.stringify(paymentData),
    }),
};

export const reportsApi = {
  getDailyAppointments: (date) =>
    request(`/reports/daily-appointments?report_date=${date}`),
  getRevenue: (startDate, endDate) =>
    request(`/reports/revenue?start_date=${startDate}&end_date=${endDate}`),
};
