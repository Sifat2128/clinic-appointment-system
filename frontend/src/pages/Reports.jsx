import React, { useState, useEffect } from 'react';
import { reportsApi } from '../api/client';

export default function Reports() {
  const [activeTab, setActiveTab] = useState('daily');
  const [dailyDate, setDailyDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [dailyReport, setDailyReport] = useState(null);
  const [loadingDaily, setLoadingDaily] = useState(false);

  const [startDate, setStartDate] = useState(() => {
    const d = new Date();
    d.setDate(d.getDate() - 30);
    return d.toISOString().split('T')[0];
  });
  const [endDate, setEndDate] = useState(() => new Date().toISOString().split('T')[0]);
  const [revenueReport, setRevenueReport] = useState(null);
  const [loadingRevenue, setLoadingRevenue] = useState(false);

  const [error, setError] = useState('');

  const fetchDailyReport = async (date) => {
    try {
      setLoadingDaily(true);
      setError('');
      const data = await reportsApi.getDailyAppointments(date);
      setDailyReport(data);
    } catch (err) {
      setError(err.message || 'Failed to generate daily report');
    } finally {
      setLoadingDaily(false);
    }
  };

  const fetchRevenueReport = async (sDate, eDate) => {
    try {
      setLoadingRevenue(true);
      setError('');
      const data = await reportsApi.getRevenue(sDate, eDate);
      setRevenueReport(data);
    } catch (err) {
      setError(err.message || 'Failed to generate revenue report');
    } finally {
      setLoadingRevenue(false);
    }
  };

  useEffect(() => {
    fetchDailyReport(dailyDate);
    fetchRevenueReport(startDate, endDate);
  }, []);

  return (
    <div className="page-container" data-testid="reports-page">
      <div className="page-header">
        <div>
          <h1>Clinical Analytics & Reports</h1>
          <p className="page-subtitle">Executive summaries generated via Factory Pattern Report Generators</p>
        </div>
      </div>

      {error && <div className="alert alert-danger">{error}</div>}

      <div className="tab-navigation">
        <button
          className={`tab-btn ${activeTab === 'daily' ? 'active' : ''}`}
          onClick={() => setActiveTab('daily')}
          data-testid="tab-daily-report"
        >
          Daily Appointments Summary
        </button>
        <button
          className={`tab-btn ${activeTab === 'revenue' ? 'active' : ''}`}
          onClick={() => setActiveTab('revenue')}
          data-testid="tab-revenue-report"
        >
          Revenue & Financial Analytics
        </button>
      </div>

      {activeTab === 'daily' ? (
        <div className="card">
          <div className="card-header flex-between">
            <h3>Daily Operations Report</h3>
            <div className="report-filter-bar">
              <input
                type="date"
                value={dailyDate}
                onChange={(e) => setDailyDate(e.target.value)}
                data-testid="report-date-input"
              />
              <button
                className="btn btn-primary btn-sm"
                onClick={() => fetchDailyReport(dailyDate)}
                data-testid="generate-daily-report-btn"
                disabled={loadingDaily}
              >
                {loadingDaily ? 'Generating...' : 'Refresh Report'}
              </button>
            </div>
          </div>
          <div className="card-body">
            {dailyReport ? (
              <div className="report-results">
                <div className="stats-grid">
                  <div className="stat-card">
                    <span className="stat-value">{dailyReport.total_appointments}</span>
                    <span className="stat-label">Total Appointments</span>
                  </div>
                  <div className="stat-card">
                    <span className="stat-value text-green">{dailyReport.completed_appointments}</span>
                    <span className="stat-label">Completed Consultations</span>
                  </div>
                  <div className="stat-card">
                    <span className="stat-value text-orange">{dailyReport.scheduled_appointments}</span>
                    <span className="stat-label">Upcoming / Scheduled</span>
                  </div>
                  <div className="stat-card">
                    <span className="stat-value text-red">{dailyReport.cancelled_appointments}</span>
                    <span className="stat-label">Cancelled Appointments</span>
                  </div>
                </div>

                <div className="report-highlight-box">
                  <p>
                    <strong>Completion Rate:</strong> {dailyReport.completion_rate_percentage}%
                  </p>
                  <p className="text-muted text-sm">
                    Generated on {new Date(dailyReport.generated_at).toLocaleString()}
                  </p>
                </div>
              </div>
            ) : (
              <p className="empty-message">No report generated.</p>
            )}
          </div>
        </div>
      ) : (
        <div className="card">
          <div className="card-header flex-between">
            <h3>Revenue & Collections Analysis</h3>
            <div className="report-filter-bar">
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                data-testid="revenue-start-date"
              />
              <span>to</span>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                data-testid="revenue-end-date"
              />
              <button
                className="btn btn-primary btn-sm"
                onClick={() => fetchRevenueReport(startDate, endDate)}
                data-testid="generate-revenue-report-btn"
                disabled={loadingRevenue}
              >
                {loadingRevenue ? 'Calculating...' : 'Run Analytics'}
              </button>
            </div>
          </div>
          <div className="card-body">
            {revenueReport ? (
              <div className="report-results">
                <div className="stats-grid">
                  <div className="stat-card">
                    <span className="stat-value">${Number(revenueReport.total_gross_revenue).toFixed(2)}</span>
                    <span className="stat-label">Gross Billed</span>
                  </div>
                  <div className="stat-card">
                    <span className="stat-value text-orange">-${Number(revenueReport.total_discounts_granted).toFixed(2)}</span>
                    <span className="stat-label">Discounts Granted</span>
                  </div>
                  <div className="stat-card">
                    <span className="stat-value text-green">${Number(revenueReport.total_net_revenue).toFixed(2)}</span>
                    <span className="stat-label">Net Collected Revenue</span>
                  </div>
                  <div className="stat-card">
                    <span className="stat-value">{revenueReport.invoices_settled_count}</span>
                    <span className="stat-label">Settled Invoices</span>
                  </div>
                </div>

                <div className="payment-breakdown-section">
                  <h4>Collections Breakdown by Payment Method</h4>
                  <div className="method-pill-grid">
                    <div className="method-pill">
                      <span>💳 Credit/Debit Card</span>
                      <strong>${Number(revenueReport.revenue_by_method?.CARD || 0).toFixed(2)}</strong>
                    </div>
                    <div className="method-pill">
                      <span>💵 Cash Over Counter</span>
                      <strong>${Number(revenueReport.revenue_by_method?.CASH || 0).toFixed(2)}</strong>
                    </div>
                    <div className="method-pill">
                      <span>📱 Mobile Banking</span>
                      <strong>${Number(revenueReport.revenue_by_method?.MOBILE_BANKING || 0).toFixed(2)}</strong>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <p className="empty-message">No financial data retrieved for the selected window.</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
