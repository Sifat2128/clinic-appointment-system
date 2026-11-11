import React, { useState, useEffect } from 'react';
import { patientsApi } from '../api/client';

export default function Patients() {
  const [patients, setPatients] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    date_of_birth: '1995-05-15',
    gender: 'MALE',
    blood_group: 'O+',
    address: '123 University Road',
    emergency_contact: '555-999-000',
  });

  const fetchPatients = async (searchTerm = '') => {
    try {
      setLoading(true);
      const data = await patientsApi.getAll(searchTerm);
      setPatients(data);
    } catch (err) {
      setError('Failed to fetch patients list');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatients();
  }, []);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchPatients(search);
  };

  const handleCreatePatient = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    try {
      await patientsApi.create(formData);
      setSuccess('Patient successfully registered!');
      setShowModal(false);
      setFormData({
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        date_of_birth: '1995-05-15',
        gender: 'MALE',
        blood_group: 'O+',
        address: '123 University Road',
        emergency_contact: '555-999-000',
      });
      fetchPatients(search);
    } catch (err) {
      setError(err.message || 'Failed to register patient');
    }
  };

  const handleDeletePatient = async (id) => {
    if (!window.confirm(`Are you sure you want to delete patient #${id}?`)) return;
    try {
      await patientsApi.delete(id);
      setSuccess(`Patient #${id} removed successfully.`);
      fetchPatients(search);
    } catch (err) {
      setError(err.message || 'Could not delete patient.');
    }
  };

  return (
    <div className="page-container" data-testid="patients-page">
      <div className="page-header">
        <div>
          <h1>Patient Management</h1>
          <p className="page-subtitle">View, search, and register patient medical demographic records</p>
        </div>
        <button
          className="btn btn-primary"
          onClick={() => setShowModal(true)}
          data-testid="open-add-patient-modal"
        >
          + Register Patient
        </button>
      </div>

      {error && <div className="alert alert-danger" data-testid="patient-error">{error}</div>}
      {success && <div className="alert alert-success" data-testid="patient-success">{success}</div>}

      <div className="search-bar-container">
        <form onSubmit={handleSearchSubmit} className="search-form">
          <input
            type="text"
            placeholder="Search by name, phone, or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="search-input"
            data-testid="patient-search"
          />
          <button type="submit" className="btn btn-secondary" data-testid="patient-search-btn">
            Search
          </button>
          {search && (
            <button
              type="button"
              className="btn btn-outline"
              onClick={() => {
                setSearch('');
                fetchPatients('');
              }}
            >
              Clear
            </button>
          )}
        </form>
      </div>

      <div className="card">
        <div className="card-body">
          {loading ? (
            <div className="loading-state">Loading patient records...</div>
          ) : patients.length === 0 ? (
            <p className="empty-message">No patients found matching the criteria.</p>
          ) : (
            <table className="data-table" data-testid="patients-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Full Name</th>
                  <th>Phone</th>
                  <th>Email</th>
                  <th>Gender</th>
                  <th>DOB</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {patients.map((p) => (
                  <tr key={p.id} data-testid={`patient-row-${p.id}`}>
                    <td>#{p.id}</td>
                    <td><strong>{p.first_name} {p.last_name}</strong></td>
                    <td>{p.phone}</td>
                    <td>{p.email}</td>
                    <td>{p.gender}</td>
                    <td>{p.date_of_birth}</td>
                    <td>
                      <button
                        className="btn-action-delete"
                        onClick={() => handleDeletePatient(p.id)}
                        data-testid={`delete-patient-${p.id}`}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {showModal && (
        <div className="modal-backdrop">
          <div className="modal-dialog">
            <div className="modal-header">
              <h3>Register New Patient</h3>
              <button className="btn-close" onClick={() => setShowModal(false)}>×</button>
            </div>
            <form onSubmit={handleCreatePatient}>
              <div className="modal-body form-grid">
                <div className="form-group">
                  <label>First Name *</label>
                  <input
                    type="text"
                    required
                    data-testid="patient-first-name"
                    value={formData.first_name}
                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Last Name *</label>
                  <input
                    type="text"
                    required
                    data-testid="patient-last-name"
                    value={formData.last_name}
                    onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Email Address *</label>
                  <input
                    type="email"
                    required
                    data-testid="patient-email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Phone Number *</label>
                  <input
                    type="tel"
                    required
                    data-testid="patient-phone"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Date of Birth *</label>
                  <input
                    type="date"
                    required
                    data-testid="patient-dob"
                    value={formData.date_of_birth}
                    onChange={(e) => setFormData({ ...formData, date_of_birth: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Gender *</label>
                  <select
                    data-testid="patient-gender"
                    value={formData.gender}
                    onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                  >
                    <option value="MALE">Male</option>
                    <option value="FEMALE">Female</option>
                    <option value="OTHER">Other</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Blood Group</label>
                  <input
                    type="text"
                    data-testid="patient-blood-group"
                    value={formData.blood_group}
                    onChange={(e) => setFormData({ ...formData, blood_group: e.target.value })}
                  />
                </div>
                <div className="form-group">
                  <label>Address</label>
                  <input
                    type="text"
                    data-testid="patient-address"
                    value={formData.address}
                    onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-outline" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary" data-testid="save-patient-btn">
                  Save Patient Record
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
