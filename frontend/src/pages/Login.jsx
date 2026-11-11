import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  const handleFillDemo = (demoEmail, demoPassword) => {
    setEmail(demoEmail);
    setPassword(demoPassword);
    setError('');
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-header">
          <div className="clinic-logo">🏥</div>
          <h2>MedFlow Clinic</h2>
          <p className="subtitle">University Hospital Appointment System</p>
        </div>

        {error && (
          <div className="alert alert-danger" data-testid="login-error">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              id="email"
              type="email"
              data-testid="email-input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="e.g. receptionist@clinic.com"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              data-testid="password-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary btn-block"
            data-testid="login-button"
            disabled={loading}
          >
            {loading ? 'Authenticating...' : 'Sign In'}
          </button>
        </form>

        <div className="demo-accounts">
          <p className="demo-title">Quick Demo Login:</p>
          <div className="demo-buttons">
            <button
              type="button"
              className="btn-demo"
              onClick={() => handleFillDemo('receptionist@clinic.com', 'Reception123!')}
            >
              Receptionist
            </button>
            <button
              type="button"
              className="btn-demo"
              onClick={() => handleFillDemo('admin@clinic.com', 'Admin123!')}
            >
              Admin
            </button>
            <button
              type="button"
              className="btn-demo"
              onClick={() => handleFillDemo('dr.sarah@clinic.com', 'Doctor123!')}
            >
              Doctor
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
