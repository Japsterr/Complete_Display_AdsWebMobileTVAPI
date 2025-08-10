import React, { useState, useEffect } from 'react';
import { fetchCampaigns, assignCampaignToDisplay, fetchDisplays, requestActivationCode } from '../services/api';
import type { Campaign, Display } from '../services/api';
import api from '../services/api';

const DisplayManagementPage: React.FC = () => {
  const [displays, setDisplays] = useState<Display[]>([]);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [activationCode, setActivationCode] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [location, setLocation] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<'success' | 'error'>('success');
  const [tvDeviceId, setTvDeviceId] = useState('TV-TEST-001');
  const [activationInfo, setActivationInfo] = useState<{ code?: string; expires?: number | null; status?: string }>({});
  const [countdown, setCountdown] = useState<number | null>(null);
  const [countdownTimer, setCountdownTimer] = useState<number | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      console.log('Loading display and campaign data...');
      const [displaysData, campaignsData] = await Promise.all([
        fetchDisplays(),
        fetchCampaigns()
      ]);
      console.log('Loaded displays:', displaysData);
      console.log('Loaded campaigns:', campaignsData);
      setDisplays(displaysData);
      setCampaigns(campaignsData);
    } catch (error) {
      console.error('Error loading data:', error);
    }
  };

  const handleCampaignAssignment = async (displayId: number, campaignId: number) => {
    console.log('Handling campaign assignment:', { displayId, campaignId });
    
    try {
      const updatedDisplay = await assignCampaignToDisplay(displayId, campaignId);
      console.log('Updated display received:', updatedDisplay);
      showMessage('Campaign assigned successfully!', 'success');
      await loadData(); // Refresh the display list to show updated campaign
    } catch (error: any) {
      console.error('Campaign assignment error:', error);
      const errorMessage = error.response?.data?.error || 'Failed to assign campaign';
      showMessage(errorMessage, 'error');
    }
  };

  const handleActivateDevice = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!activationCode.trim()) {
      showMessage('Please enter an activation code', 'error');
      return;
    }

    setLoading(true);
    try {
      const response = await api.post('/devices/activate/', {
        activation_code: activationCode.toUpperCase(),
        display_name: displayName || `TV-${activationCode}`,
        location: location || 'Unspecified Location'
      });

      showMessage(response.data.message, 'success');
      setActivationCode('');
      setDisplayName('');
      setLocation('');
      await loadData(); // Refresh the list
    } catch (error: any) {
      const errorMessage = error.response?.data?.error || 'Failed to activate device';
      showMessage(errorMessage, 'error');
    } finally {
      setLoading(false);
    }
  };

  const showMessage = (text: string, type: 'success' | 'error') => {
    setMessage(text);
    setMessageType(type);
    setTimeout(() => setMessage(''), 5000);
  };

  const loadActivationCode = async () => {
    try {
      const res = await requestActivationCode(tvDeviceId, { source: 'web-dashboard' });
      const expires = typeof res.expires_in_seconds === 'number' ? res.expires_in_seconds : null;
      setActivationInfo({ code: res.activation_code, expires, status: res.status });
      if (countdownTimer) window.clearInterval(countdownTimer);
      if (expires !== null) {
        setCountdown(expires);
        const id = window.setInterval(() => {
          setCountdown(prev => {
            const next = prev !== null ? Math.max(0, prev - 1) : null;
            if (next === 0) {
              window.clearInterval(id);
              loadActivationCode();
            }
            return next;
          });
        }, 1000);
        setCountdownTimer(id);
      } else {
        setCountdown(null);
      }
    } catch (e) {
      showMessage('Failed to request activation code', 'error');
    }
  };

  return (
    <div className="container-fluid py-4">
      <div className="row">
        <div className="col-12">
          <h1 className="h3 mb-4 text-gray-800">Display Management</h1>
        </div>
      </div>

      {/* Activate New Device */}
      <div className="row mb-4">
        <div className="col-lg-6">
          <div className="card shadow">
            <div className="card-header">
              <h5 className="card-title mb-0">Register New Display</h5>
            </div>
            <div className="card-body">
              {message && (
                <div className={`alert ${messageType === 'success' ? 'alert-success' : 'alert-danger'} alert-dismissible fade show`} role="alert">
                  {message}
                  <button 
                    type="button" 
                    className="btn-close" 
                    onClick={() => setMessage('')}
                    aria-label="Close"
                  ></button>
                </div>
              )}

              <form onSubmit={handleActivateDevice}>
                <div className="mb-3">
                  <label htmlFor="activationCode" className="form-label">
                    Activation Code <span className="text-danger">*</span>
                  </label>
                  <input
                    type="text"
                    className="form-control"
                    id="activationCode"
                    placeholder="Enter 6-character code from TV screen"
                    value={activationCode}
                    onChange={(e) => setActivationCode(e.target.value.toUpperCase())}
                    maxLength={6}
                    style={{ fontFamily: 'monospace', fontSize: '1.2rem', letterSpacing: '0.2rem' }}
                    required
                  />
                  <div className="form-text">
                    This code is displayed on your TV screen
                  </div>
                </div>

                <div className="mb-3">
                  <label htmlFor="displayName" className="form-label">Display Name</label>
                  <input
                    type="text"
                    className="form-control"
                    id="displayName"
                    placeholder="e.g., Reception TV, Conference Room Display"
                    value={displayName}
                    onChange={(e) => setDisplayName(e.target.value)}
                  />
                </div>

                <div className="mb-3">
                  <label htmlFor="location" className="form-label">Location</label>
                  <input
                    type="text"
                    className="form-control"
                    id="location"
                    placeholder="e.g., Main Office, Building A Lobby"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                  />
                </div>

                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={loading}
                >
                  {loading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      Activating...
                    </>
                  ) : (
                    'Activate Display'
                  )}
                </button>
              </form>
            </div>
          </div>
        </div>

        <div className="col-lg-6">
          <div className="card shadow">
            <div className="card-header">
              <h5 className="card-title mb-0">Activation Instructions</h5>
            </div>
            <div className="card-body">
              <ol className="mb-0">
                <li className="mb-2">
                  <strong>Install the TV App:</strong> Install the Digital Signage app on your Android TV device.
                </li>
                <li className="mb-2">
                  <strong>Launch the App:</strong> Open the app on your TV. It will show a 6-character activation code.
                </li>
                <li className="mb-2">
                  <strong>Enter the Code:</strong> Type the activation code from your TV screen into the form on the left.
                </li>
                <li className="mb-2">
                  <strong>Complete Registration:</strong> Give your display a name and location, then click "Activate Display".
                </li>
                <li>
                  <strong>Start Using:</strong> Your TV will automatically start displaying your content!
                </li>
              </ol>
              <hr />
              <div className="row g-2 align-items-end">
                <div className="col-sm-6">
                  <label className="form-label">Device ID (from TV)</label>
                  <input className="form-control" value={tvDeviceId} onChange={e=>setTvDeviceId(e.target.value)} placeholder="TV-TEST-001" />
                </div>
                <div className="col-sm-3">
                  <button className="btn btn-outline-primary w-100" onClick={loadActivationCode}>Get Code</button>
                </div>
                <div className="col-sm-3">
                  <div className="text-end small text-muted">
                    {activationInfo.code ? (
                      <>
                        <div><strong>Code:</strong> <span style={{fontFamily:'monospace'}}>{activationInfo.code}</span></div>
                        {countdown !== null && <div>Expires in: {countdown}s</div>}
                      </>
                    ) : (
                      <div>—</div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Active Displays */}
      <div className="row">
        <div className="col-12">
          <div className="card shadow">
            <div className="card-header">
              <h5 className="card-title mb-0">Active Displays ({displays.length})</h5>
            </div>
            <div className="card-body">
              {displays.length === 0 ? (
                <div className="text-center py-4">
                  <div className="text-muted">
                    <i className="fas fa-tv fa-3x mb-3 d-block"></i>
                    <p>No displays registered yet.</p>
                    <p>Use the form above to register your first display.</p>
                  </div>
                </div>
              ) : (
                <div className="table-responsive">
                  <table className="table table-hover">
                    <thead>
                      <tr>
                        <th>Name</th>
                        <th>Location</th>
                        <th>Device ID</th>
                        <th>Status</th>
                        <th>Current Campaign</th>
                        <th>Registered</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {displays.map((display) => (
                        <tr key={display.display_id}>
                          <td>
                            <strong>{display.name}</strong>
                          </td>
                          <td>{display.location || 'Not specified'}</td>
                          <td>
                            <code className="small">{display.device_id}</code>
                          </td>
                          <td>
                            <span className={`badge ${
                              display.activation_status === 'activated' ? 'bg-success' : 
                              display.activation_status === 'pending' ? 'bg-warning' : 'bg-secondary'
                            }`}>
                              {display.activation_status}
                            </span>
                          </td>
                          <td>{display.default_campaign_name || 'None'}</td>
                          <td>{display.registered_at ? new Date(display.registered_at).toLocaleDateString() : '-'}</td>
                          <td>
                            <div className="btn-group" role="group">
                              <select 
                                className="form-select form-select-sm"
                                value={display.default_campaign || ''}
                                onChange={(e) => {
                                  const campaignId = e.target.value;
                                  if (campaignId) {
                                    handleCampaignAssignment(display.display_id, parseInt(campaignId));
                                  } else {
                                    // Handle clearing campaign (set to null)
                                    handleCampaignAssignment(display.display_id, 0); // 0 will be treated as null
                                  }
                                }}
                                style={{ maxWidth: '200px' }}
                              >
                                <option value="">No Campaign</option>
                                {campaigns.map((campaign) => (
                                  <option key={campaign.campaign_id} value={campaign.campaign_id}>
                                    {campaign.name}
                                  </option>
                                ))}
                              </select>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DisplayManagementPage;
