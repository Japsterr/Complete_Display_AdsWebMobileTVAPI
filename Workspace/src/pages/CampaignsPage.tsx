import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { PlusIcon, PencilIcon, TrashIcon, FilmIcon } from "@heroicons/react/24/outline";
import api from "../services/api.ts";

function StatusBadge({ status }: { status: string }) {
  const statusConfig = {
    draft: { className: "badge bg-light text-dark", icon: "📝", text: "Draft" },
    ready: { className: "badge bg-info text-white", icon: "✅", text: "Ready" },
    active: { className: "badge bg-success text-white", icon: "🟢", text: "Active" },
    paused: { className: "badge bg-warning text-dark", icon: "⏸️", text: "Paused" },
    scheduled: { className: "badge bg-primary text-white", icon: "⏰", text: "Scheduled" },
    expired: { className: "badge bg-danger text-white", icon: "❌", text: "Expired" },
  };
  
  const safeStatus = status || 'draft';
  const config = statusConfig[safeStatus as keyof typeof statusConfig] || statusConfig.draft;
  
  return (
    <span className={config.className}>
      <span className="me-1">{config.icon}</span>
      {config.text}
    </span>
  );
}

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");
  const navigate = useNavigate();

  useEffect(() => {
    api.get("/campaigns/")
      .then(res => {
        setCampaigns(res.data);
        setLoading(false);
      })
      .catch(err => {
        setError(`Failed to load campaigns: ${err.message}`);
        setLoading(false);
      });
  }, []);

  const handleDelete = async (id: number) => {
    if (confirm("Are you sure you want to delete this campaign?")) {
      try {
        await api.delete(`/campaigns/${id}/`);
        setCampaigns(campaigns.filter(c => c.campaign_id !== id));
      } catch (err: any) {
        setError(`Failed to delete campaign: ${err.message}`);
      }
    }
  };

  return (
    <div className="container-fluid py-4">
      {/* Page Header */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h1 className="h3 mb-1">Campaigns</h1>
          <p className="text-muted mb-0">Create and manage your digital signage campaigns.</p>
        </div>
        <button
          type="button"
          className="btn btn-primary"
          onClick={() => navigate("/campaigns/new")}
        >
          <PlusIcon style={{ width: '16px', height: '16px' }} className="me-2" />
          Create Campaign
        </button>
      </div>

      {/* Content */}
      {loading ? (
        <div className="d-flex justify-content-center py-5">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      ) : error ? (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      ) : campaigns.length === 0 ? (
        <div className="card">
          <div className="card-body text-center py-5">
            <PlusIcon style={{ width: '64px', height: '64px' }} className="text-muted mb-3" />
            <h4 className="card-title">No Campaigns Yet</h4>
            <p className="card-text text-muted mb-4">
              Start creating engaging campaigns for your digital signage displays.
            </p>
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => navigate("/campaigns/new")}
            >
              <PlusIcon style={{ width: '16px', height: '16px' }} className="me-2" />
              Create Your First Campaign
            </button>
          </div>
        </div>
      ) : (
        <div className="card">
          <div className="card-header bg-white">
            <h5 className="card-title mb-0">All Campaigns</h5>
          </div>
          <div className="card-body p-0">
            <div className="table-responsive">
              <table className="table table-hover mb-0">
                <thead className="table-light">
                  <tr>
                    <th className="px-4 py-3">Campaign</th>
                    <th className="px-3 py-3">Status</th>
                    <th className="px-3 py-3 text-center">Media</th>
                    <th className="px-3 py-3">Orientation</th>
                    <th className="px-3 py-3">Schedule</th>
                    <th className="px-3 py-3">Created</th>
                    <th className="px-4 py-3 text-end">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {campaigns.map((campaign) => (
                    <tr key={campaign.campaign_id}>
                      <td className="px-4 py-3">
                        <div>
                          <div className="fw-semibold">{campaign.name}</div>
                          {campaign.description && (
                            <small className="text-muted">{campaign.description}</small>
                          )}
                        </div>
                      </td>
                      <td className="px-3 py-3">
                        <StatusBadge status={campaign.status} />
                      </td>
                      <td className="px-3 py-3 text-center">
                        <div className="fw-semibold">{campaign.media_count || 0}</div>
                        <small className="text-muted">
                          {campaign.total_duration ? `${campaign.total_duration}s` : '0s'}
                        </small>
                      </td>
                      <td className="px-3 py-3">
                        <div>
                          <small className="text-muted">Screen:</small>{' '}
                          <span className="badge bg-secondary me-2">{campaign.screen_orientation || 'portrait'}</span>
                          <small className="text-muted">Normalize:</small>{' '}
                          <span className="badge bg-light text-dark">{campaign.normalize_to_orientation || 'none'}</span>
                        </div>
                      </td>
                      <td className="px-3 py-3">
                        <div className="small">
                          {campaign.start_date ? (
                            <>
                              <div className="text-success">
                                📅 {new Date(campaign.start_date).toLocaleDateString()}
                              </div>
                              {campaign.end_date && (
                                <div className="text-danger">
                                  ⏰ {new Date(campaign.end_date).toLocaleDateString()}
                                </div>
                              )}
                            </>
                          ) : (
                            <span className="text-muted">Not scheduled</span>
                          )}
                        </div>
                      </td>
                      <td className="px-3 py-3">
                        <small className="text-muted">
                          {campaign.created_at ? new Date(campaign.created_at).toLocaleDateString() : 'N/A'}
                        </small>
                      </td>
                      <td className="px-4 py-3 text-end">
                        <div className="btn-group btn-group-sm" role="group">
                          <button
                            type="button"
                            className="btn btn-outline-primary"
                            onClick={() => navigate(`/campaigns/${campaign.campaign_id}/edit`)}
                            title="Edit Campaign"
                          >
                            <PencilIcon style={{ width: '14px', height: '14px' }} />
                          </button>
                          <button
                            type="button"
                            className="btn btn-outline-secondary"
                            onClick={() => navigate(`/campaigns/${campaign.campaign_id}/media`)}
                            title="Manage Media"
                          >
                            <FilmIcon style={{ width: '14px', height: '14px' }} />
                          </button>
                          <button
                            type="button"
                            className="btn btn-outline-danger"
                            onClick={() => handleDelete(campaign.campaign_id)}
                            title="Delete Campaign"
                          >
                            <TrashIcon style={{ width: '14px', height: '14px' }} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
