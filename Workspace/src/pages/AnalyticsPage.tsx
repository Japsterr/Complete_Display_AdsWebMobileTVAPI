import { useState, useEffect } from 'react';
import api from '../services/api';

interface DeviceStatus {
  display_id: number;
  name: string;
  status: string;
  last_seen: string | null;
  current_campaign: string | null;
}

interface CampaignPerformance {
  [campaignName: string]: {
    total_impressions: number;
    total_duration: number;
    unique_displays: number;
  };
}

interface RecentImpression {
  timestamp: string;
  display: string;
  campaign: string;
  media: string;
  duration: number;
  completed: boolean;
}

interface AnalyticsData {
  device_status: DeviceStatus[];
  campaign_performance: CampaignPerformance;
  recent_impressions: RecentImpression[];
}

const AnalyticsPage = () => {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = async () => {
    try {
      const response = await api.get('/analytics/dashboard/');
      setAnalyticsData(response.data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to fetch analytics data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
    
    // Refresh data every 30 seconds
    const interval = setInterval(fetchAnalytics, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  if (loading) {
    return (
      <div className="container-fluid py-4">
        <div className="text-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p className="mt-2">Loading analytics data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container-fluid py-4">
        <div className="alert alert-danger" role="alert">
          <h4 className="alert-heading">Error loading analytics</h4>
          <p>{error}</p>
          <button className="btn btn-outline-danger" onClick={fetchAnalytics}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!analyticsData) {
    return (
      <div className="container-fluid py-4">
        <div className="alert alert-info" role="alert">
          No analytics data available
        </div>
      </div>
    );
  }

  return (
    <div className="container-fluid py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Analytics Dashboard</h1>
        <button className="btn btn-outline-primary" onClick={fetchAnalytics}>
          <i className="fas fa-sync-alt me-2"></i>
          Refresh
        </button>
      </div>

      {/* Summary Cards */}
      <div className="row mb-4">
        <div className="col-md-3">
          <div className="card bg-primary text-white">
            <div className="card-body">
              <div className="d-flex justify-content-between">
                <div>
                  <h5 className="card-title">Total Devices</h5>
                  <h2>{analyticsData.device_status.length}</h2>
                </div>
                <div className="align-self-center">
                  <i className="fas fa-tv fa-2x"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-success text-white">
            <div className="card-body">
              <div className="d-flex justify-content-between">
                <div>
                  <h5 className="card-title">Active Devices</h5>
                  <h2>{analyticsData.device_status.filter(d => d.status === 'online').length}</h2>
                </div>
                <div className="align-self-center">
                  <i className="fas fa-check-circle fa-2x"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-info text-white">
            <div className="card-body">
              <div className="d-flex justify-content-between">
                <div>
                  <h5 className="card-title">Total Impressions</h5>
                  <h2>{analyticsData.recent_impressions.length}</h2>
                </div>
                <div className="align-self-center">
                  <i className="fas fa-eye fa-2x"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card bg-warning text-white">
            <div className="card-body">
              <div className="d-flex justify-content-between">
                <div>
                  <h5 className="card-title">Campaigns</h5>
                  <h2>{Object.keys(analyticsData.campaign_performance).length}</h2>
                </div>
                <div className="align-self-center">
                  <i className="fas fa-bullhorn fa-2x"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Device Status Table */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="card">
            <div className="card-header">
              <h5 className="card-title mb-0">Device Status</h5>
            </div>
            <div className="card-body">
              {analyticsData.device_status.length === 0 ? (
                <p className="text-muted">No device data available</p>
              ) : (
                <div className="table-responsive">
                  <table className="table table-striped">
                    <thead>
                      <tr>
                        <th>Device ID</th>
                        <th>Device Name</th>
                        <th>Status</th>
                        <th>Last Seen</th>
                        <th>Current Campaign</th>
                      </tr>
                    </thead>
                    <tbody>
                      {analyticsData.device_status.map((device) => (
                        <tr key={device.display_id}>
                          <td>
                            <code>{device.display_id}</code>
                          </td>
                          <td>{device.name}</td>
                          <td>
                            <span className={`badge ${
                              device.status === 'online' ? 'bg-success' : 'bg-secondary'
                            }`}>
                              {device.status}
                            </span>
                          </td>
                          <td>{device.last_seen ? formatDateTime(device.last_seen) : 'Never'}</td>
                          <td>{device.current_campaign || 'No Campaign'}</td>
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

      {/* Campaign Statistics */}
      <div className="row mb-4">
        <div className="col-12">
          <div className="card">
            <div className="card-header">
              <h5 className="card-title mb-0">Campaign Performance</h5>
            </div>
            <div className="card-body">
              {Object.keys(analyticsData.campaign_performance).length === 0 ? (
                <p className="text-muted">No campaign data available</p>
              ) : (
                <div className="table-responsive">
                  <table className="table table-striped">
                    <thead>
                      <tr>
                        <th>Campaign</th>
                        <th>Total Impressions</th>
                        <th>Unique Devices</th>
                        <th>Total Duration</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(analyticsData.campaign_performance).map(([campaignName, stats]) => (
                        <tr key={campaignName}>
                          <td>{campaignName}</td>
                          <td>
                            <span className="badge bg-primary">
                              {stats.total_impressions}
                            </span>
                          </td>
                          <td>{stats.unique_displays}</td>
                          <td>{formatDuration(stats.total_duration)}</td>
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

      {/* Recent Impressions */}
      <div className="row">
        <div className="col-12">
          <div className="card">
            <div className="card-header">
              <h5 className="card-title mb-0">Recent Impressions</h5>
            </div>
            <div className="card-body">
              {analyticsData.recent_impressions.length === 0 ? (
                <p className="text-muted">No recent impressions available</p>
              ) : (
                <div className="table-responsive">
                  <table className="table table-striped">
                    <thead>
                      <tr>
                        <th>Timestamp</th>
                        <th>Display</th>
                        <th>Campaign</th>
                        <th>Media</th>
                        <th>Duration</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {analyticsData.recent_impressions.map((impression, index) => (
                        <tr key={index}>
                          <td>{formatDateTime(impression.timestamp)}</td>
                          <td>{impression.display}</td>
                          <td>{impression.campaign}</td>
                          <td>{impression.media}</td>
                          <td>{formatDuration(impression.duration)}</td>
                          <td>
                            <span className={`badge ${
                              impression.completed ? 'bg-success' : 'bg-warning'
                            }`}>
                              {impression.completed ? 'Completed' : 'In Progress'}
                            </span>
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

export default AnalyticsPage;
