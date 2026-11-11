import React, { useState, useEffect } from 'react';
import { billingApi } from '../api/client';

export default function Billing() {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedInvoice, setSelectedInvoice] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [submitting, setSubmitting] = useState(false);

  // Payment form state
  const [discountType, setDiscountType] = useState('STUDENT');
  const [paymentMethod, setPaymentMethod] = useState('CARD');
  const [cardNumber, setCardNumber] = useState('4532000000001234');
  const [mobileNumber, setMobileNumber] = useState('01700000000');
  const [receivedBy, setReceivedBy] = useState('Reception Cash Desk');

  const fetchInvoices = async () => {
    try {
      setLoading(true);
      const data = await billingApi.getInvoices();
      setInvoices(data);
    } catch (err) {
      setError('Failed to fetch invoice records');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvoices();
  }, []);

  const handleOpenPayModal = (inv) => {
    setSelectedInvoice(inv);
    setError('');
    setSuccess('');
  };

  const handleProcessPayment = async (e) => {
    e.preventDefault();
    if (!selectedInvoice) return;
    setSubmitting(true);
    setError('');
    setSuccess('');

    try {
      const payload = {
        discount_type: discountType,
        payment_method: paymentMethod,
        card_number: paymentMethod === 'CARD' ? cardNumber : undefined,
        mobile_number: paymentMethod === 'MOBILE_BANKING' ? mobileNumber : undefined,
        received_by: paymentMethod === 'CASH' ? receivedBy : undefined,
      };

      const result = await billingApi.payInvoice(selectedInvoice.id, payload);
      setSuccess(
        `Payment successful! Transaction Ref: ${result.transaction_reference} | Net Paid: $${Number(result.net_amount).toFixed(2)}`
      );
      setSelectedInvoice(null);
      fetchInvoices();
    } catch (err) {
      setError(err.data?.detail || err.message || 'Payment processing failed');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="page-container" data-testid="billing-page">
      <div className="page-header">
        <div>
          <h1>Billing & Payments</h1>
          <p className="page-subtitle">Invoice management powered by Strategy discounts & Factory payments</p>
        </div>
      </div>

      {error && <div className="alert alert-danger" data-testid="billing-error">{error}</div>}
      {success && <div className="alert alert-success" data-testid="billing-success">{success}</div>}

      <div className="card">
        <div className="card-header">
          <h3>Invoices Ledger</h3>
        </div>
        <div className="card-body">
          {loading ? (
            <div className="loading-state">Loading invoices...</div>
          ) : invoices.length === 0 ? (
            <p className="empty-message">No invoices generated yet.</p>
          ) : (
            <table className="data-table" data-testid="invoices-table">
              <thead>
                <tr>
                  <th>Invoice #</th>
                  <th>Appointment #</th>
                  <th>Patient #</th>
                  <th>Gross Amount</th>
                  <th>Discount</th>
                  <th>Net Payable</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {invoices.map((inv) => (
                  <tr key={inv.id} data-testid={`invoice-row-${inv.id}`}>
                    <td><strong>#{inv.id}</strong></td>
                    <td>Apt #{inv.appointment_id}</td>
                    <td>Patient #{inv.patient_id}</td>
                    <td>${Number(inv.gross_amount).toFixed(2)}</td>
                    <td>
                      {inv.discount_type ? (
                        <span className="discount-tag">{inv.discount_type} (${Number(inv.discount_amount).toFixed(2)})</span>
                      ) : (
                        'None'
                      )}
                    </td>
                    <td><strong>${Number(inv.net_amount).toFixed(2)}</strong></td>
                    <td>
                      <span className={`status-badge status-${inv.status.toLowerCase()}`}>
                        {inv.status}
                      </span>
                    </td>
                    <td>
                      {inv.status === 'PENDING' ? (
                        <button
                          className="btn btn-primary btn-sm"
                          onClick={() => handleOpenPayModal(inv)}
                          data-testid={`pay-invoice-btn-${inv.id}`}
                        >
                          Checkout
                        </button>
                      ) : (
                        <span className="text-muted text-sm">Settled ({inv.payment_method})</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {selectedInvoice && (
        <div className="modal-backdrop">
          <div className="modal-dialog">
            <div className="modal-header">
              <h3>Checkout Invoice #{selectedInvoice.id}</h3>
              <button className="btn-close" onClick={() => setSelectedInvoice(null)}>×</button>
            </div>
            <form onSubmit={handleProcessPayment}>
              <div className="modal-body form-grid">
                <div className="invoice-summary-box">
                  <p>Initial Consultation Fee: <strong>${Number(selectedInvoice.gross_amount).toFixed(2)}</strong></p>
                </div>

                <div className="form-group">
                  <label htmlFor="select-discount">Discount Strategy (Strategy Pattern) *</label>
                  <select
                    id="select-discount"
                    data-testid="select-discount"
                    value={discountType}
                    onChange={(e) => setDiscountType(e.target.value)}
                  >
                    <option value="NONE">No Discount (0%)</option>
                    <option value="STUDENT">Student Discount (18%)</option>
                    <option value="SENIOR_CITIZEN">Senior Citizen Discount (15%)</option>
                    <option value="INSURANCE">Healthcare Insurance (80%)</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="select-payment-method">Payment Processor (Factory Pattern) *</label>
                  <select
                    id="select-payment-method"
                    data-testid="select-payment-method"
                    value={paymentMethod}
                    onChange={(e) => setPaymentMethod(e.target.value)}
                  >
                    <option value="CARD">Credit/Debit Card (Bank Gateway)</option>
                    <option value="CASH">Cash Over The Counter</option>
                    <option value="MOBILE_BANKING">Mobile Banking (bKash/Nagad)</option>
                  </select>
                </div>

                {paymentMethod === 'CARD' && (
                  <div className="form-group">
                    <label>Card Number (Visa / Mastercard)</label>
                    <input
                      type="text"
                      data-testid="input-card-number"
                      value={cardNumber}
                      onChange={(e) => setCardNumber(e.target.value)}
                      placeholder="4532 0000 0000 1234"
                      required
                    />
                  </div>
                )}

                {paymentMethod === 'MOBILE_BANKING' && (
                  <div className="form-group">
                    <label>Mobile Wallet Number</label>
                    <input
                      type="text"
                      value={mobileNumber}
                      onChange={(e) => setMobileNumber(e.target.value)}
                      placeholder="017xxxxxxxx"
                      required
                    />
                  </div>
                )}

                {paymentMethod === 'CASH' && (
                  <div className="form-group">
                    <label>Receptionist Desk Identifier</label>
                    <input
                      type="text"
                      value={receivedBy}
                      onChange={(e) => setReceivedBy(e.target.value)}
                      placeholder="Desk 1 Receptionist"
                      required
                    />
                  </div>
                )}
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-outline"
                  onClick={() => setSelectedInvoice(null)}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn btn-primary"
                  data-testid="submit-payment-btn"
                  disabled={submitting}
                >
                  {submitting ? 'Authorizing Payment...' : 'Confirm & Pay Invoice'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
