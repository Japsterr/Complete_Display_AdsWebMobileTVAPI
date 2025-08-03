import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeftIcon, PlusIcon, TrashIcon, ArrowUpIcon, ArrowDownIcon } from "@heroicons/react/24/outline";
import api from "../services/api.ts";

type Media = {
  media_id: number;
  file: string;
  name: string;
  description?: string;
  uploaded_at: string;
};

type CampaignMedia = {
  campaign_media_id: number;
  campaign: number;
  media: number;
  display_duration_seconds: number;
  order: number;
  media_details?: Media; // Populated by frontend
};

type Campaign = {
  campaign_id: number;
  name: string;
  description?: string;
  created_at: string;
};

export default function CampaignMediaEditor() {
  const { campaignId } = useParams<{ campaignId: string }>();
  const navigate = useNavigate();
  
  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [campaignMedia, setCampaignMedia] = useState<CampaignMedia[]>([]);
  const [availableMedia, setAvailableMedia] = useState<Media[]>([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);

  useEffect(() => {
    if (!campaignId) return;

    // Load campaign details
    api.get(`/campaigns/${campaignId}/`)
      .then(res => setCampaign(res.data))
      .catch(console.error);

    // Load campaign media
    api.get(`/campaign-media/?campaign=${campaignId}`)
      .then(res => {
        console.log("Campaign media response:", res.data);
        setCampaignMedia(res.data);
      })
      .catch(console.error);

    // Load available media
    api.get("/media/")
      .then(res => setAvailableMedia(res.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [campaignId]);

  const handleAddMedia = async (mediaId: number, duration: number = 10) => {
    try {
      const maxOrder = Math.max(...campaignMedia.map(cm => cm.order), -1);
      const response = await api.post("/campaign-media/", {
        campaign: parseInt(campaignId!),
        media: mediaId,
        display_duration_seconds: duration,
        order: maxOrder + 1
      });
      
      // Add media details to the response
      const mediaDetails = availableMedia.find(m => m.media_id === mediaId);
      const newCampaignMedia = { ...response.data, media_details: mediaDetails };
      
      setCampaignMedia([...campaignMedia, newCampaignMedia]);
      setShowAddModal(false);
    } catch (error) {
      console.error("Error adding media to campaign:", error);
      alert("Failed to add media to campaign");
    }
  };

  const handleRemoveMedia = async (campaignMediaId: number) => {
    if (confirm("Remove this media from the campaign?")) {
      try {
        await api.delete(`/campaign-media/${campaignMediaId}/`);
        setCampaignMedia(campaignMedia.filter(cm => cm.campaign_media_id !== campaignMediaId));
      } catch (error) {
        console.error("Error removing media:", error);
        alert("Failed to remove media");
      }
    }
  };

  const handleUpdateDuration = async (campaignMediaId: number, newDuration: number) => {
    try {
      await api.patch(`/campaign-media/${campaignMediaId}/`, {
        display_duration_seconds: newDuration
      });
      
      setCampaignMedia(campaignMedia.map(cm => 
        cm.campaign_media_id === campaignMediaId 
          ? { ...cm, display_duration_seconds: newDuration }
          : cm
      ));
    } catch (error) {
      console.error("Error updating duration:", error);
      alert("Failed to update duration");
    }
  };

  const handleDurationInputChange = (campaignMediaId: number, value: string) => {
    // Update local state immediately
    setCampaignMedia(campaignMedia.map(cm => 
      cm.campaign_media_id === campaignMediaId 
        ? { ...cm, display_duration_seconds: parseInt(value) || 10 }
        : cm
    ));
  };

  const handleDurationBlur = (campaignMediaId: number, value: string) => {
    // Save to server on blur
    const duration = parseInt(value) || 10;
    handleUpdateDuration(campaignMediaId, duration);
  };

  const moveMedia = async (campaignMediaId: number, direction: 'up' | 'down') => {
    const currentIndex = campaignMedia.findIndex(cm => cm.campaign_media_id === campaignMediaId);
    if (currentIndex === -1) return;

    const newIndex = direction === 'up' ? currentIndex - 1 : currentIndex + 1;
    if (newIndex < 0 || newIndex >= campaignMedia.length) return;

    const newOrder = [...campaignMedia];
    [newOrder[currentIndex], newOrder[newIndex]] = [newOrder[newIndex], newOrder[currentIndex]];
    
    // Update orders
    newOrder[currentIndex].order = currentIndex;
    newOrder[newIndex].order = newIndex;

    try {
      await Promise.all([
        api.patch(`/campaign-media/${newOrder[currentIndex].campaign_media_id}/`, { order: currentIndex }),
        api.patch(`/campaign-media/${newOrder[newIndex].campaign_media_id}/`, { order: newIndex })
      ]);
      
      setCampaignMedia(newOrder);
    } catch (error) {
      console.error("Error reordering media:", error);
      alert("Failed to reorder media");
    }
  };

  if (loading) {
    return (
      <div className="container-fluid">
        <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '400px' }}>
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      </div>
    );
  }

  // Get media details for campaign media items
  const campaignMediaWithDetails = campaignMedia.map(cm => ({
    ...cm,
    media_details: availableMedia.find(m => m.media_id === cm.media)
  }));

  const availableMediaForAdd = availableMedia.filter(media => 
    !campaignMedia.some(cm => cm.media === media.media_id)
  );

  return (
    <div className="container-fluid">
      {/* Header */}
      <div className="d-flex align-items-center mb-4">
        <button 
          className="btn btn-outline-secondary me-3"
          onClick={() => navigate('/dashboard/campaigns')}
        >
          <ArrowLeftIcon style={{ width: '16px', height: '16px' }} />
        </button>
        <div>
          <h1 className="h2 mb-1">Campaign Media Editor</h1>
          <p className="text-muted mb-0">
            {campaign ? `Editing: ${campaign.name}` : 'Loading campaign...'}
          </p>
        </div>
      </div>

      {/* Campaign Playlist */}
      <div className="row">
        <div className="col-lg-8">
          <div className="card">
            <div className="card-header d-flex justify-content-between align-items-center">
              <h5 className="mb-0">Campaign Playlist</h5>
              <button 
                className="btn btn-primary btn-sm"
                onClick={() => setShowAddModal(true)}
                disabled={availableMediaForAdd.length === 0}
              >
                <PlusIcon style={{ width: '16px', height: '16px' }} className="me-1" />
                Add Media
              </button>
            </div>
            <div className="card-body">
              {campaignMediaWithDetails.length === 0 ? (
                <div className="text-center py-5">
                  <PlusIcon style={{ width: '64px', height: '64px' }} className="text-muted mb-3" />
                  <h4>No Media in Campaign</h4>
                  <p className="text-muted mb-4">
                    Add media files to create your campaign playlist.
                  </p>
                  <button 
                    className="btn btn-primary"
                    onClick={() => setShowAddModal(true)}
                    disabled={availableMediaForAdd.length === 0}
                  >
                    <PlusIcon style={{ width: '16px', height: '16px' }} className="me-2" />
                    Add First Media
                  </button>
                  {availableMediaForAdd.length === 0 && (
                    <p className="text-muted mt-3">
                      <small>Upload media files first in the Media Library</small>
                    </p>
                  )}
                </div>
              ) : (
                <div className="list-group list-group-flush">
                  {campaignMediaWithDetails
                    .sort((a, b) => a.order - b.order)
                    .map((item, index) => (
                    <div key={item.campaign_media_id} className="list-group-item d-flex align-items-center">
                      <div className="d-flex flex-column me-3">
                        <button 
                          className="btn btn-outline-secondary btn-sm mb-1"
                          onClick={() => moveMedia(item.campaign_media_id, 'up')}
                          disabled={index === 0}
                        >
                          <ArrowUpIcon style={{ width: '12px', height: '12px' }} />
                        </button>
                        <button 
                          className="btn btn-outline-secondary btn-sm"
                          onClick={() => moveMedia(item.campaign_media_id, 'down')}
                          disabled={index === campaignMediaWithDetails.length - 1}
                        >
                          <ArrowDownIcon style={{ width: '12px', height: '12px' }} />
                        </button>
                      </div>
                      
                      <div className="me-3" style={{ width: '80px', height: '60px' }}>
                        {item.media_details ? (
                          <img 
                            src={item.media_details.file}
                            alt={item.media_details.name}
                            className="img-thumbnail w-100 h-100"
                            style={{ objectFit: 'cover' }}
                          />
                        ) : (
                          <div className="bg-light d-flex align-items-center justify-content-center w-100 h-100">
                            <span className="text-muted">?</span>
                          </div>
                        )}
                      </div>
                      
                      <div className="flex-grow-1">
                        <h6 className="mb-1">{item.media_details?.name || `Media ${item.media}`}</h6>
                        <small className="text-muted">Order: {item.order + 1}</small>
                      </div>
                      
                      <div className="me-3">
                        <label className="form-label small">Duration (seconds)</label>
                        <input 
                          type="number"
                          className="form-control form-control-sm"
                          value={item.display_duration_seconds}
                          onChange={(e) => handleDurationInputChange(item.campaign_media_id, e.target.value)}
                          onBlur={(e) => handleDurationBlur(item.campaign_media_id, e.target.value)}
                          min="1"
                          max="300"
                          style={{ width: '80px' }}
                        />
                      </div>
                      
                      <button 
                        className="btn btn-outline-danger btn-sm"
                        onClick={() => handleRemoveMedia(item.campaign_media_id)}
                      >
                        <TrashIcon style={{ width: '16px', height: '16px' }} />
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="col-lg-4">
          <div className="card">
            <div className="card-header">
              <h6 className="mb-0">Campaign Info</h6>
            </div>
            <div className="card-body">
              {campaign ? (
                <>
                  <p><strong>Name:</strong> {campaign.name}</p>
                  {campaign.description && (
                    <p><strong>Description:</strong> {campaign.description}</p>
                  )}
                  <p><strong>Created:</strong> {new Date(campaign.created_at).toLocaleDateString()}</p>
                  <p><strong>Media Count:</strong> {campaignMedia.length}</p>
                  <p><strong>Total Duration:</strong> {campaignMedia.reduce((total, cm) => total + cm.display_duration_seconds, 0)} seconds</p>
                </>
              ) : (
                <p className="text-muted">Loading campaign info...</p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Add Media Modal */}
      {showAddModal && (
        <div className="modal fade show d-block" style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}>
          <div className="modal-dialog modal-lg">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Add Media to Campaign</h5>
                <button 
                  type="button" 
                  className="btn-close" 
                  onClick={() => setShowAddModal(false)}
                ></button>
              </div>
              <div className="modal-body">
                {availableMediaForAdd.length === 0 ? (
                  <p className="text-muted text-center py-4">
                    All available media is already in this campaign.
                  </p>
                ) : (
                  <div className="row g-3">
                    {availableMediaForAdd.map(media => (
                      <div key={media.media_id} className="col-md-6">
                        <div className="card">
                          <div className="position-relative" style={{ paddingBottom: "56.25%" }}>
                            <img 
                              src={media.file}
                              alt={media.name}
                              className="card-img-top position-absolute w-100 h-100"
                              style={{ objectFit: 'cover' }}
                            />
                          </div>
                          <div className="card-body">
                            <h6 className="card-title">{media.name}</h6>
                            <div className="d-flex align-items-center">
                              <input 
                                type="number"
                                className="form-control form-control-sm me-2"
                                placeholder="Duration (sec)"
                                min="1"
                                max="300"
                                defaultValue="10"
                                id={`duration-${media.media_id}`}
                                style={{ width: '100px' }}
                              />
                              <button 
                                className="btn btn-primary btn-sm"
                                onClick={() => {
                                  const durationInput = document.getElementById(`duration-${media.media_id}`) as HTMLInputElement;
                                  const duration = parseInt(durationInput.value) || 10;
                                  handleAddMedia(media.media_id, duration);
                                }}
                              >
                                Add
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={() => setShowAddModal(false)}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
