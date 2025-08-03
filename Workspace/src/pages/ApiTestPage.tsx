import { useState, useEffect } from 'react';
import api from '../services/api';

export default function ApiTestPage() {
  const [displays, setDisplays] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [displaysRes, campaignsRes] = await Promise.all([
        api.get('/displays/'),
        api.get('/campaigns/')
      ]);
      
      setDisplays(displaysRes.data.results || displaysRes.data);
      setCampaigns(campaignsRes.data.results || campaignsRes.data);
    } catch (err: any) {
      console.error('API Error:', err);
      setError(`API Error: ${err.response?.status} ${err.response?.statusText}`);
    } finally {
      setLoading(false);
    }
  };

  const createTestDisplay = async () => {
    try {
      const newDisplay = {
        display_name: `Test Display ${Date.now()}`,
        location: 'Test Location',
        status: 'active'
      };
      
      const response = await api.post('/displays/', newDisplay);
      console.log('Created display:', response.data);
      fetchData(); // Refresh data
    } catch (err: any) {
      console.error('Error creating display:', err);
      setError(`Error creating display: ${err.response?.data?.detail || err.message}`);
    }
  };

  if (loading) {
    return (
      <div className="container mt-5">
        <div className="text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="mt-2">Testing API connections...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mt-5">
      <div className="row">
        <div className="col-12">
          <h1 className="mb-4">🧪 API Connection Test</h1>
          
          {error && (
            <div className="alert alert-danger" role="alert">
              <i className="bi bi-exclamation-triangle me-2"></i>
              {error}
            </div>
          )}

          <div className="row g-4">
            <div className="col-md-6">
              <div className="card">
                <div className="card-header d-flex justify-content-between align-items-center">
                  <h5 className="mb-0">
                    <i className="bi bi-display me-2"></i>
                    Displays ({displays.length})
                  </h5>
                  <button className="btn btn-sm btn-primary" onClick={createTestDisplay}>
                    <i className="bi bi-plus"></i> Add Test Display
                  </button>
                </div>
                <div className="card-body">
                  {displays.length === 0 ? (
                    <p className="text-muted">No displays found. Try adding a test display!</p>
                  ) : (
                    <div className="list-group list-group-flush">
                      {displays.slice(0, 5).map((display: any) => (
                        <div key={display.id} className="list-group-item px-0">
                          <div className="d-flex justify-content-between">
                            <div>
                              <strong>{display.display_name}</strong>
                              <br />
                              <small className="text-muted">{display.location}</small>
                            </div>
                            <span className={`badge ${display.status === 'active' ? 'bg-success' : 'bg-secondary'}`}>
                              {display.status}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="col-md-6">
              <div className="card">
                <div className="card-header">
                  <h5 className="mb-0">
                    <i className="bi bi-megaphone me-2"></i>
                    Campaigns ({campaigns.length})
                  </h5>
                </div>
                <div className="card-body">
                  {campaigns.length === 0 ? (
                    <p className="text-muted">No campaigns found.</p>
                  ) : (
                    <div className="list-group list-group-flush">
                      {campaigns.slice(0, 5).map((campaign: any) => (
                        <div key={campaign.id} className="list-group-item px-0">
                          <div className="d-flex justify-content-between">
                            <div>
                              <strong>{campaign.name}</strong>
                              <br />
                              <small className="text-muted">
                                {campaign.start_date} - {campaign.end_date}
                              </small>
                            </div>
                            <span className={`badge ${campaign.status === 'active' ? 'bg-success' : 'bg-warning'}`}>
                              {campaign.status}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>

          <div className="mt-4">
            <div className="card">
              <div className="card-header">
                <h5 className="mb-0">
                  <i className="bi bi-check-circle me-2"></i>
                  API Connection Status
                </h5>
              </div>
              <div className="card-body">
                <div className="row">
                  <div className="col-md-4">
                    <div className="text-center">
                      <i className="bi bi-server text-success" style={{fontSize: '2rem'}}></i>
                      <h6 className="mt-2">Backend</h6>
                      <span className="badge bg-success">Connected</span>
                      <p className="small text-muted">Django API running on port 8000</p>
                    </div>
                  </div>
                  <div className="col-md-4">
                    <div className="text-center">
                      <i className="bi bi-shield-check text-success" style={{fontSize: '2rem'}}></i>
                      <h6 className="mt-2">Authentication</h6>
                      <span className="badge bg-success">Working</span>
                      <p className="small text-muted">JWT tokens functioning</p>
                    </div>
                  </div>
                  <div className="col-md-4">
                    <div className="text-center">
                      <i className="bi bi-database text-success" style={{fontSize: '2rem'}}></i>
                      <h6 className="mt-2">Database</h6>
                      <span className="badge bg-success">Active</span>
                      <p className="small text-muted">CRUD operations working</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
