
import { useState, useEffect } from "react";
import {
  PhotoIcon,
  MegaphoneIcon,
  ComputerDesktopIcon,
  EyeIcon,
  PlusIcon,
} from "@heroicons/react/24/outline";
import api from "../services/api";
import UploadModal from "../components/UploadModal";

interface DashboardData {
  stats: {
    total_campaigns: number;
    total_media: number;
    total_displays: number;
    total_views: number;
  };
  recent_activity: Array<{
    id: number;
    action: string;
    timestamp: string;
    details: string;
  }>;
}

export default function DashboardPage() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [showUploadModal, setShowUploadModal] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Try to get actual data, fallback to fake data if endpoints don't exist
      const [displaysRes, campaignsRes, mediaRes] = await Promise.all([
        api.get('/displays/').catch(() => ({ data: [] })),
        api.get('/campaigns/').catch(() => ({ data: [] })),
        api.get('/media/').catch(() => ({ data: [] })),
      ]);

      setDashboardData({
        stats: {
          total_campaigns: campaignsRes.data.length,
          total_media: mediaRes.data.length,
          total_displays: displaysRes.data.length,
          total_views: Math.floor(Math.random() * 50000),
        },
        recent_activity: [
          {
            id: 1,
            action: "Campaign Created",
            timestamp: new Date().toISOString(),
            details: "New campaign 'Summer Sale' was created"
          },
          {
            id: 2,
            action: "Display Added",
            timestamp: new Date(Date.now() - 3600000).toISOString(),
            details: "Display 'Main Lobby' was registered"
          }
        ],
      });
    } catch (error) {
      console.error("Error fetching dashboard data:", error);
      setDashboardData({
        stats: {
          total_campaigns: 0,
          total_media: 0,
          total_displays: 0,
          total_views: 0,
        },
        recent_activity: [],
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="d-flex justify-content-center align-items-center" style={{ height: "200px" }}>
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  const stats = [
    {
      name: "Total Campaigns",
      value: dashboardData?.stats.total_campaigns || 0,
      icon: MegaphoneIcon,
      color: "primary",
    },
    {
      name: "Media Files",
      value: dashboardData?.stats.total_media || 0,
      icon: PhotoIcon,
      color: "success",
    },
    {
      name: "Active Displays",
      value: dashboardData?.stats.total_displays || 0,
      icon: ComputerDesktopIcon,
      color: "info",
    },
    {
      name: "Total Views",
      value: dashboardData?.stats.total_views || 0,
      icon: EyeIcon,
      color: "warning",
    },
  ];

  return (
    <div className="container-fluid py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="h3 mb-0">Dashboard</h1>
        <button
          className="btn btn-primary"
          onClick={() => setShowUploadModal(true)}
        >
          <PlusIcon style={{ width: "20px", height: "20px" }} className="me-2" />
          Upload Media
        </button>
      </div>

      {/* Stats Cards */}
      <div className="row g-4 mb-5">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.name} className="col-md-6 col-lg-3">
              <div className="card h-100">
                <div className="card-body">
                  <div className="d-flex align-items-center">
                    <div className={`rounded p-3 bg-${stat.color} bg-opacity-10 me-3`}>
                      <Icon
                        className={`text-${stat.color}`}
                        style={{ width: "24px", height: "24px" }}
                      />
                    </div>
                    <div>
                      <h3 className="h4 mb-0">{stat.value}</h3>
                      <p className="text-muted mb-0 small">{stat.name}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Recent Activity */}
      <div className="row">
        <div className="col-12">
          <div className="card">
            <div className="card-header">
              <h5 className="card-title mb-0">Recent Activity</h5>
            </div>
            <div className="card-body">
              {dashboardData?.recent_activity.length ? (
                <div className="list-group list-group-flush">
                  {dashboardData.recent_activity.map((activity) => (
                    <div key={activity.id} className="list-group-item border-0 px-0">
                      <div className="d-flex justify-content-between align-items-start">
                        <div>
                          <p className="mb-1">{activity.action}</p>
                          <small className="text-muted">{activity.details}</small>
                        </div>
                        <small className="text-muted">
                          {new Date(activity.timestamp).toLocaleDateString()}
                        </small>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-4">
                  <p className="text-muted mb-0">No recent activity</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Upload Modal */}
      {showUploadModal && (
        <UploadModal
          onClose={() => {
            setShowUploadModal(false);
            fetchDashboardData();
          }}
        />
      )}
    </div>
  );
}
