import { useState, useEffect } from 'react';
import { 
  ChartBarIcon, 
  TvIcon, 
  EyeIcon, 
  PlayIcon,
  CalendarIcon,
  ClockIcon
} from '@heroicons/react/24/outline';
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

interface ImpressionSummary {
  campaign: string;
  media_name: string;
  display_count: number;
  total_impressions: number;
  total_duration: number;
  completion_rate: number;
  last_played: string;
}

interface DeviceSummary {
  display_name: string;
  display_id: number;
  total_impressions: number;
  unique_campaigns: number;
  total_watch_time: number;
  last_activity: string;
  status: string;
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
    const interval = setInterval(fetchAnalytics, 30000);
    return () => clearInterval(interval);
  }, []);

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const formatDuration = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes}m`;
    } else if (minutes > 0) {
      return `${minutes}m`;
    } else {
      return `${seconds}s`;
    }
  };

  // Create summarized data from impressions
  const getImpressionSummary = (): ImpressionSummary[] => {
    if (!analyticsData?.recent_impressions) return [];

    const summary = new Map<string, ImpressionSummary>();

    analyticsData.recent_impressions.forEach(impression => {
      const key = `${impression.campaign}-${impression.media}`;
      
      if (!summary.has(key)) {
        summary.set(key, {
          campaign: impression.campaign,
          media_name: impression.media,
          display_count: new Set([impression.display]).size,
          total_impressions: 0,
          total_duration: 0,
          completion_rate: 0,
          last_played: impression.timestamp
        });
      }

      const item = summary.get(key)!;
      item.total_impressions += 1;
      item.total_duration += impression.duration;
      
      if (new Date(impression.timestamp) > new Date(item.last_played)) {
        item.last_played = impression.timestamp;
      }
    });

    // Calculate completion rates and display counts
    analyticsData.recent_impressions.forEach(impression => {
      const key = `${impression.campaign}-${impression.media}`;
      const item = summary.get(key)!;
      
      const displays = new Set(
        analyticsData.recent_impressions
          .filter(i => i.campaign === impression.campaign && i.media === impression.media)
          .map(i => i.display)
      );
      item.display_count = displays.size;

      const completedCount = analyticsData.recent_impressions
        .filter(i => i.campaign === impression.campaign && i.media === impression.media && i.completed)
        .length;
      item.completion_rate = (completedCount / item.total_impressions) * 100;
    });

    return Array.from(summary.values()).sort((a, b) => b.total_impressions - a.total_impressions);
  };

  // Create device summary
  const getDeviceSummary = (): DeviceSummary[] => {
    if (!analyticsData?.recent_impressions || !analyticsData?.device_status) return [];

    const deviceMap = new Map<string, DeviceSummary>();

    // Initialize with device status
    analyticsData.device_status.forEach(device => {
      deviceMap.set(device.name, {
        display_name: device.name,
        display_id: device.display_id,
        total_impressions: 0,
        unique_campaigns: 0,
        total_watch_time: 0,
        last_activity: device.last_seen || 'Never',
        status: device.status
      });
    });

    // Aggregate impression data
    analyticsData.recent_impressions.forEach(impression => {
      if (!deviceMap.has(impression.display)) {
        deviceMap.set(impression.display, {
          display_name: impression.display,
          display_id: 0,
          total_impressions: 0,
          unique_campaigns: 0,
          total_watch_time: 0,
          last_activity: impression.timestamp,
          status: 'unknown'
        });
      }

      const device = deviceMap.get(impression.display)!;
      device.total_impressions += 1;
      device.total_watch_time += impression.duration;

      if (new Date(impression.timestamp) > new Date(device.last_activity)) {
        device.last_activity = impression.timestamp;
      }
    });

    // Calculate unique campaigns per device
    deviceMap.forEach((device, displayName) => {
      const campaigns = new Set(
        analyticsData.recent_impressions
          .filter(i => i.display === displayName)
          .map(i => i.campaign)
      );
      device.unique_campaigns = campaigns.size;
    });

    return Array.from(deviceMap.values()).sort((a, b) => b.total_impressions - a.total_impressions);
  };

  if (loading) {
    return (
      <div className="container-fluid py-4">
        <div className="d-flex justify-content-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
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

  const impressionSummary = getImpressionSummary();
  const deviceSummary = getDeviceSummary();
  const totalImpressions = analyticsData.recent_impressions.length;
  const totalWatchTime = analyticsData.recent_impressions.reduce((sum, imp) => sum + imp.duration, 0);

  return (
    <div className="container-fluid py-4">
      {/* Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="h3 mb-1">Analytics Dashboard</h1>
          <p className="text-muted mb-0">Overview of your digital signage performance</p>
        </div>
        <button className="btn btn-outline-primary" onClick={fetchAnalytics}>
          <CalendarIcon style={{ width: '16px', height: '16px' }} className="me-2" />
          Refresh
        </button>
      </div>

      {/* Summary Cards */}
      <div className="row g-4 mb-4">
        <div className="col-md-3">
          <div className="card h-100">
            <div className="card-body">
              <div className="d-flex align-items-center">
                <div className="flex-shrink-0">
                  <div className="bg-primary bg-opacity-10 rounded-circle p-3">
                    <TvIcon style={{ width: '24px', height: '24px' }} className="text-primary" />
                  </div>
                </div>
                <div className="flex-grow-1 ms-3">
                  <h3 className="h5 mb-1">{analyticsData.device_status.length}</h3>
                  <p className="text-muted mb-0">Total Displays</p>
                  <small className="text-success">
                    {analyticsData.device_status.filter(d => d.status === 'online').length} online
                  </small>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="col-md-3">
          <div className="card h-100">
            <div className="card-body">
              <div className="d-flex align-items-center">
                <div className="flex-shrink-0">
                  <div className="bg-success bg-opacity-10 rounded-circle p-3">
                    <EyeIcon style={{ width: '24px', height: '24px' }} className="text-success" />
                  </div>
                </div>
                <div className="flex-grow-1 ms-3">
                  <h3 className="h5 mb-1">{totalImpressions.toLocaleString()}</h3>
                  <p className="text-muted mb-0">Total Impressions</p>
                  <small className="text-muted">All time</small>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="col-md-3">
          <div className="card h-100">
            <div className="card-body">
              <div className="d-flex align-items-center">
                <div className="flex-shrink-0">
                  <div className="bg-info bg-opacity-10 rounded-circle p-3">
                    <ClockIcon style={{ width: '24px', height: '24px' }} className="text-info" />
                  </div>
                </div>
                <div className="flex-grow-1 ms-3">
                  <h3 className="h5 mb-1">{formatDuration(totalWatchTime)}</h3>
                  <p className="text-muted mb-0">Total Watch Time</p>
                  <small className="text-muted">All displays</small>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="col-md-3">
          <div className="card h-100">
            <div className="card-body">
              <div className="d-flex align-items-center">
                <div className="flex-shrink-0">
                  <div className="bg-warning bg-opacity-10 rounded-circle p-3">
                    <PlayIcon style={{ width: '24px', height: '24px' }} className="text-warning" />
                  </div>
                </div>
                <div className="flex-grow-1 ms-3">
                  <h3 className="h5 mb-1">{Object.keys(analyticsData.campaign_performance).length}</h3>
                  <p className="text-muted mb-0">Active Campaigns</p>
                  <small className="text-muted">Running now</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Content Summary */}
      <div className="row g-4 mb-4">
        <div className="col-lg-8">
          <div className="card">
            <div className="card-header bg-white">
              <h5 className="card-title mb-0">
                <ChartBarIcon style={{ width: '20px', height: '20px' }} className="me-2" />
                Content Performance Summary
              </h5>
            </div>
            <div className="card-body p-0">
              {impressionSummary.length === 0 ? (
                <div className="text-center py-5">
                  <p className="text-muted">No content impressions yet</p>
                </div>
              ) : (
                <div className="table-responsive">
                  <table className="table table-hover mb-0">
                    <thead className="table-light">
                      <tr>
                        <th className="px-4 py-3">Content</th>
                        <th className="px-3 py-3">Campaign</th>
                        <th className="px-3 py-3 text-center">Impressions</th>
                        <th className="px-3 py-3 text-center">Displays</th>
                        <th className="px-3 py-3 text-center">Total Time</th>
                        <th className="px-3 py-3 text-center">Completion</th>
                      </tr>
                    </thead>
                    <tbody>
                      {impressionSummary.slice(0, 10).map((item, index) => (
                        <tr key={index}>
                          <td className="px-4 py-3">
                            <div className="fw-semibold">{item.media_name}</div>
                            <small className="text-muted">Last played: {formatDateTime(item.last_played)}</small>
                          </td>
                          <td className="px-3 py-3">
                            <span className="badge bg-primary text-white">
                              {item.campaign}
                            </span>
                          </td>
                          <td className="px-3 py-3 text-center">
                            <span className="fw-semibold">{item.total_impressions}</span>
                          </td>
                          <td className="px-3 py-3 text-center">
                            <span className="text-muted">{item.display_count}</span>
                          </td>
                          <td className="px-3 py-3 text-center">
                            <span className="text-muted">{formatDuration(item.total_duration)}</span>
                          </td>
                          <td className="px-3 py-3 text-center">
                            <span className={`badge ${item.completion_rate >= 80 ? 'bg-success' : item.completion_rate >= 50 ? 'bg-warning' : 'bg-danger'}`}>
                              {item.completion_rate.toFixed(0)}%
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

        <div className="col-lg-4">
          <div className="card">
            <div className="card-header bg-white">
              <h5 className="card-title mb-0">
                <TvIcon style={{ width: '20px', height: '20px' }} className="me-2" />
                Display Performance
              </h5>
            </div>
            <div className="card-body p-0">
              {deviceSummary.length === 0 ? (
                <div className="text-center py-5">
                  <p className="text-muted">No display data yet</p>
                </div>
              ) : (
                <div className="list-group list-group-flush">
                  {deviceSummary.slice(0, 8).map((device, index) => (
                    <div key={index} className="list-group-item">
                      <div className="d-flex justify-content-between align-items-start">
                        <div className="flex-grow-1">
                          <div className="d-flex align-items-center mb-1">
                            <h6 className="mb-0 me-2">{device.display_name}</h6>
                            <span className={`badge badge-sm ${device.status === 'online' ? 'bg-success' : 'bg-secondary'}`}>
                              {device.status}
                            </span>
                          </div>
                          <div className="small text-muted">
                            <div>📺 {device.total_impressions} impressions</div>
                            <div>🎬 {device.unique_campaigns} campaigns</div>
                            <div>⏱️ {formatDuration(device.total_watch_time)} total</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
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
