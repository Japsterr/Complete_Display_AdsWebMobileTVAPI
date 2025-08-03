import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api.ts";

export default function RegisterDisplayPage() {
  const [form, setForm] = useState({ name: "", location: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    
    try {
      const response = await api.post("/displays/", form);
      console.log("Display registered successfully:", response.data);
      navigate("/displays");
    } catch (err: any) {
      console.error("Failed to register display:", err);
      setError(err.response?.data?.detail || "Failed to register display. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="container-fluid">
      <div className="row justify-content-center">
        <div className="col-lg-8">
          <div className="mb-4">
            <h1 className="h2 mb-1">Register New Display</h1>
            <p className="text-muted">Add a new display to your network.</p>
          </div>

          <div className="card">
            <div className="card-header">
              <h5 className="card-title mb-0">Display Information</h5>
            </div>
            <div className="card-body">
              <form onSubmit={handleSubmit}>
                <div className="row">
                  <div className="col-md-6">
                    <div className="mb-3">
                      <label htmlFor="display_name" className="form-label">
                        Display Name <span className="text-danger">*</span>
                      </label>
                      <input
                        type="text"
                        className="form-control"
                        id="display_name"
                        name="display_name"
                        value={form.name}
                        onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                        placeholder="e.g., Lobby Display"
                        required
                      />
                      <div className="form-text">Choose a descriptive name for this display</div>
                    </div>
                  </div>
                  <div className="col-md-6">
                    <div className="mb-3">
                      <label htmlFor="location" className="form-label">
                        Location <span className="text-danger">*</span>
                      </label>
                      <input
                        type="text"
                        className="form-control"
                        id="location"
                        name="location"
                        value={form.location}
                        onChange={e => setForm(f => ({ ...f, location: e.target.value }))}
                        placeholder="e.g., Main Lobby, Store Front"
                        required
                      />
                      <div className="form-text">Where is this display physically located?</div>
                    </div>
                  </div>
                </div>

                {error && (
                  <div className="alert alert-danger" role="alert">
                    <i className="bi bi-exclamation-triangle me-2"></i>
                    {error}
                  </div>
                )}

                <div className="d-flex gap-2 justify-content-end">
                  <button
                    type="button"
                    className="btn btn-outline-secondary"
                    onClick={() => navigate("/displays")}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={loading}
                  >
                    {loading ? "Registering..." : "Register Display"}
                  </button>
                </div>
              </form>
            </div>
          </div>

          <div className="card mt-4">
            <div className="card-header">
              <h5 className="card-title mb-0">Next Steps</h5>
            </div>
            <div className="card-body">
              <div className="row">
                <div className="col-md-6">
                  <h6>After Registration:</h6>
                  <ol className="list-group list-group-numbered list-group-flush">
                    <li className="list-group-item border-0 px-0">Download the DisplayAds player app</li>
                    <li className="list-group-item border-0 px-0">Install on your display device</li>
                    <li className="list-group-item border-0 px-0">Enter the display code to connect</li>
                  </ol>
                </div>
                <div className="col-md-6">
                  <h6>Supported Devices:</h6>
                  <ul className="list-unstyled">
                    <li><i className="bi bi-check-circle text-success me-2"></i>Android TV</li>
                    <li><i className="bi bi-check-circle text-success me-2"></i>Windows PC</li>
                    <li><i className="bi bi-check-circle text-success me-2"></i>Raspberry Pi</li>
                    <li><i className="bi bi-check-circle text-success me-2"></i>Fire TV</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
