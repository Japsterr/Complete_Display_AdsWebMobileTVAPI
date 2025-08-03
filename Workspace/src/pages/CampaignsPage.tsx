import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { PlusIcon, PencilIcon, TrashIcon, FilmIcon } from "@heroicons/react/24/outline";
import api from "../services/api.ts";

function StatusBadge({ status }: { status: string }) {
  const colors = {
    active: "bg-success",
    paused: "bg-warning", 
    draft: "bg-secondary",
  };
  
  // Default to 'draft' if status is undefined or null
  const safeStatus = status || 'draft';
  
  return (
    <span className={`badge ${colors[safeStatus as keyof typeof colors] || colors.draft}`}>
      {safeStatus.charAt(0).toUpperCase() + safeStatus.slice(1)}
    </span>
  );
}

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");
  const navigate = useNavigate();

  useEffect(() => {
    console.log("CampaignsPage: Loading campaigns...");
    console.log("Current token:", localStorage.getItem("access_token"));
    console.log("API base URL:", "http://127.0.0.1:8000/api/v1/");
    
    api.get("/campaigns/")
      .then(res => {
        console.log("CampaignsPage: API response:", res.data);
        setCampaigns(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error("CampaignsPage: API error:", err);
        console.error("Error response:", err.response);
        setError(`Failed to load campaigns: ${err.message}`);
        setLoading(false);
      });
  }, []);

  const handleDelete = async (id: number) => {
    if (confirm("Are you sure you want to delete this campaign?")) {
      try {
        await api.delete(`/campaigns/${id}/`);
        setCampaigns(campaigns.filter(c => c.campaign_id !== id));
      } catch (error) {
        console.error("Failed to delete campaign:", error);
      }
    }
  };

  return (
    <div className="container-fluid">
      <div className="d-flex justify-content-between align-items-start mb-4">
        <div>
          <h1 className="h2 mb-1">Campaigns</h1>
          <p className="text-muted">
            Create and manage your digital signage campaigns.
          </p>
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

      {loading ? (
        <div className="d-flex justify-content-center align-items-center" style={{ height: "200px" }}>
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      ) : error ? (
        <div className="alert alert-danger" role="alert">
          <h4 className="alert-heading">Error!</h4>
          <p>{error}</p>
          <button 
            className="btn btn-outline-danger" 
            onClick={() => window.location.reload()}
          >
            Try Again
          </button>
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
          <div className="card-header">
            <h5 className="card-title mb-0">All Campaigns</h5>
          </div>
          <div className="card-body p-0">
            <div className="table-responsive">
              <table className="table table-hover mb-0">
                <thead className="table-light">
                  <tr>
                    <th scope="col">Campaign</th>
                    <th scope="col">Status</th>
                    <th scope="col">Created</th>
                    <th scope="col" className="text-end">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {campaigns.map((campaign) => (
                    <tr key={campaign.campaign_id}>
                      <td>
                        <div>
                          <div className="fw-medium">{campaign.name}</div>
                          {campaign.description && (
                            <small className="text-muted">{campaign.description}</small>
                          )}
                        </div>
                      </td>
                      <td>
                        <StatusBadge status={campaign.status} />
                      </td>
                      <td>
                        <small className="text-muted">
                          {campaign.created_at ? new Date(campaign.created_at).toLocaleDateString() : 'N/A'}
                        </small>
                      </td>
                      <td className="text-end">
                        <div className="btn-group" role="group">
                          <button
                            type="button"
                            className="btn btn-outline-primary btn-sm"
                            onClick={() => navigate(`/campaigns/${campaign.campaign_id}/edit`)}
                            title="Edit Campaign"
                          >
                            <PencilIcon style={{ width: '16px', height: '16px' }} />
                          </button>
                          <button
                            type="button"
                            className="btn btn-outline-secondary btn-sm"
                            onClick={() => navigate(`/campaigns/${campaign.campaign_id}/media`)}
                            title="Edit Media Playlist"
                          >
                            <FilmIcon style={{ width: '16px', height: '16px' }} />
                          </button>
                          <button
                            type="button"
                            className="btn btn-outline-danger btn-sm"
                            onClick={() => handleDelete(campaign.campaign_id)}
                            title="Delete Campaign"
                          >
                            <TrashIcon style={{ width: '16px', height: '16px' }} />
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
