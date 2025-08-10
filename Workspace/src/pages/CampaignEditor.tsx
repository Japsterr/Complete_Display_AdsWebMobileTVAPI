import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Bars3Icon } from "@heroicons/react/24/outline";
import api from "../services/api.ts";

export default function CampaignEditor() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const isEdit = !!id;
  const [form, setForm] = useState({ name: "", description: "", screen_orientation: "portrait", normalize_to_orientation: "none" });
  const [playlist, setPlaylist] = useState<any[]>([]);
  const [showMediaModal, setShowMediaModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!isEdit) return;
    (async () => {
      try {
        const res = await api.get(`/campaigns/${id}/`);
        const c = res.data;
        setForm({
          name: c.name || "",
          description: c.description || "",
          screen_orientation: c.screen_orientation || "portrait",
          normalize_to_orientation: c.normalize_to_orientation || "none",
        });
      } catch (e: any) {
        setError(e?.response?.data?.detail || "Failed to load campaign");
      }
    })();
  }, [id, isEdit]);

  async function handleSave() {
    if (!form.name.trim()) {
      setError("Campaign name is required");
      return;
    }
    
    setLoading(true);
    setError("");
    
    try {
      if (isEdit) {
        const response = await api.patch(`/campaigns/${id}/`, {
          name: form.name,
          description: form.description || "",
          screen_orientation: form.screen_orientation,
          normalize_to_orientation: form.normalize_to_orientation,
        });
        console.log("Campaign updated successfully:", response.data);
      } else {
        const response = await api.post("/campaigns/", {
          name: form.name,
          description: form.description || "",
          screen_orientation: form.screen_orientation,
          normalize_to_orientation: form.normalize_to_orientation,
        });
        console.log("Campaign created successfully:", response.data);
      }
      navigate("/campaigns");
    } catch (err: any) {
      console.error("Failed to create campaign:", err);
      setError(err.response?.data?.detail || (isEdit ? "Failed to update campaign" : "Failed to create campaign"));
    } finally {
      setLoading(false);
    }
  }

  function handleDragStart(idx: number) {
    setPlaylist(p =>
      p.map((item, i) => ({
        ...item,
        dragging: i === idx,
      }))
    );
  }

  function handleDragEnd(idx: number, targetIdx: number) {
    const updated = [...playlist];
    const [removed] = updated.splice(idx, 1);
    updated.splice(targetIdx, 0, removed);
    setPlaylist(updated.map(item => ({ ...item, dragging: false })));
  }

  return (
    <div className="container-fluid">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1 className="h2 mb-0">{isEdit ? "Edit Campaign" : "Create New Campaign"}</h1>
        <button
          className="btn btn-primary"
          onClick={handleSave}
          disabled={loading}
        >
          {loading ? "Saving..." : isEdit ? "Save Changes" : "Save Campaign"}
        </button>
      </div>
      
      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}
      
      <div className="row">
        {/* Left Column: Form */}
        <div className="col-lg-6 mb-4">
          <div className="card">
            <div className="card-header">
              <h5 className="card-title mb-0">Campaign Details</h5>
            </div>
            <div className="card-body">
              <div className="mb-3">
                <label className="form-label">Campaign Name</label>
                <input
                  type="text"
                  className="form-control"
                  value={form.name}
                  onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                  placeholder="Enter campaign name"
                />
              </div>
              <div className="mb-3">
                <label className="form-label">Description</label>
                <textarea
                  className="form-control"
                  rows={4}
                  value={form.description}
                  onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
                  placeholder="Enter campaign description"
                />
              </div>
              <div className="row">
                <div className="col-md-6">
                  <div className="mb-3">
                    <label className="form-label">Screen Orientation</label>
                    <select
                      className="form-select"
                      value={form.screen_orientation}
                      onChange={e => setForm(f => ({ ...f, screen_orientation: e.target.value as any }))}
                    >
                      <option value="portrait">Portrait</option>
                      <option value="landscape">Landscape</option>
                    </select>
                    <small className="text-muted">Orientation intended for the media in this campaign.</small>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="mb-3">
                    <label className="form-label">Normalize To Orientation</label>
                    <select
                      className="form-select"
                      value={form.normalize_to_orientation}
                      onChange={e => setForm(f => ({ ...f, normalize_to_orientation: e.target.value as any }))}
                    >
                      <option value="none">None</option>
                      <option value="portrait">Portrait</option>
                      <option value="landscape">Landscape</option>
                    </select>
                    <small className="text-muted">Playback hint for TV app to letterbox/pillarbox to this orientation.</small>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        {/* Right Column: Playlist Builder */}
        <div className="col-lg-6 mb-4">
          <div className="card">
            <div className="card-header d-flex justify-content-between align-items-center">
              <h5 className="card-title mb-0">Playlist</h5>
              <button
                className="btn btn-outline-primary btn-sm"
                onClick={() => setShowMediaModal(true)}
              >
                Add Media
              </button>
            </div>
            <div className="card-body">
              {playlist.length === 0 ? (
                <div className="text-center text-muted py-5">
                  <p>No media added to playlist yet.</p>
                  <button
                    className="btn btn-primary"
                    onClick={() => setShowMediaModal(true)}
                  >
                    Add Your First Media
                  </button>
                </div>
              ) : (
                <div className="list-group list-group-flush">
                  {playlist.map((item, idx) => (
                    <div
                      key={item.id}
                      className={`list-group-item d-flex align-items-center ${item.dragging ? "bg-light" : ""}`}
                      draggable
                      onDragStart={() => handleDragStart(idx)}
                      onDragEnd={() => handleDragEnd(idx, idx)}
                      style={{ cursor: 'move' }}
                    >
                      <Bars3Icon style={{ width: '20px', height: '20px' }} className="text-muted me-3" />
                      <img 
                        src={item.thumbnail_url} 
                        alt={item.file_name} 
                        className="rounded me-3"
                        style={{ width: '60px', height: '40px', objectFit: 'cover' }}
                      />
                      <div className="flex-grow-1">
                        <div className="fw-medium">{item.file_name}</div>
                        <div className="d-flex align-items-center mt-1">
                          <label className="form-label small text-muted me-2 mb-0">Duration (s):</label>
                          <input
                            type="number"
                            className="form-control form-control-sm"
                            style={{ width: '80px' }}
                            value={item.duration}
                            onChange={e => {
                              const val = Number(e.target.value);
                              setPlaylist(p =>
                                p.map((media, i) =>
                                  i === idx ? { ...media, duration: val } : media
                                )
                              );
                            }}
                          />
                        </div>
                      </div>
                      <button
                        className="btn btn-outline-danger btn-sm"
                        onClick={() => setPlaylist(p => p.filter((_, i) => i !== idx))}
                      >
                        Remove
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
      {/* Media Library Modal for adding media */}
      {showMediaModal && (
        <div className="modal show d-block" style={{ zIndex: 1050 }}>
          <div className="modal-backdrop show" onClick={() => setShowMediaModal(false)}></div>
          <div className="modal-dialog modal-lg modal-dialog-centered">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">Add Media to Playlist</h5>
                <button type="button" className="btn-close" onClick={() => setShowMediaModal(false)}></button>
              </div>
              <div className="modal-body">
                <div className="text-center text-muted py-5">
                  <p>Media library integration coming soon...</p>
                  <small>You'll be able to select media files from your library here.</small>
                </div>
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowMediaModal(false)}
                >
                  Close
                </button>
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={() => setShowMediaModal(false)}
                >
                  Add Selected Media
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
