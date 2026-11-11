import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, logout, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (!isAuthenticated) return null;

  return (
    <nav className="navbar" data-testid="main-navbar">
      <div className="nav-container">
        <div className="nav-brand" onClick={() => navigate('/dashboard')}>
          <span className="brand-icon">🏥</span>
          <span className="brand-title">MedFlow Clinic</span>
        </div>

        <div className="nav-links">
          <NavLink to="/dashboard" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')} data-testid="nav-dashboard">
            Dashboard
          </NavLink>
          <NavLink to="/patients" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')} data-testid="nav-patients">
            Patients
          </NavLink>
          <NavLink to="/doctors" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')} data-testid="nav-doctors">
            Doctors & Schedules
          </NavLink>
          <NavLink to="/book-appointment" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')} data-testid="nav-book-appointment">
            Book Appointment
          </NavLink>
          <NavLink to="/billing" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')} data-testid="nav-billing">
            Billing
          </NavLink>
          <NavLink to="/reports" className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')} data-testid="nav-reports">
            Reports
          </NavLink>
        </div>

        <div className="nav-user">
          <div className="user-info">
            <span className="user-name" data-testid="nav-user-name">{user?.full_name || user?.email}</span>
            <span className="user-role-badge" data-testid="nav-user-role">{user?.role}</span>
          </div>
          <button onClick={handleLogout} className="btn-logout" data-testid="logout-button">
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}
