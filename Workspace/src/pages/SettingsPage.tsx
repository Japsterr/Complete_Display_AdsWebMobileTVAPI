import { useState, useEffect } from "react";
import api from "../services/api";

interface UserProfile {
  id: number;
  email: string;
  account_type: string;  
  first_name?: string;
  last_name?: string;
}

export default function SettingsPage() {  
  const [profile, setProfile] = useState<UserProfile>({
    id: 0,
    email: "",
    account_type: "personal",
    first_name: "",
    last_name: ""
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      const response = await api.get("/auth/profile/");
      setProfile(response.data);
    } catch (error) {
      console.error("Error fetching profile:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleProfileSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setMessage("");
    
    try {
      const response = await api.patch("/auth/profile/", {
        first_name: profile.first_name,
        last_name: profile.last_name
      });
      setProfile(response.data);
      setMessage("Profile updated successfully!");
    } catch (error) {
      console.error("Error updating profile:", error);
      setMessage("Failed to update profile");
    } finally {
      setSaving(false);
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

  return (
    <div className="container-fluid py-4">
      <div className="row justify-content-center">
        <div className="col-lg-8">
          <div className="mb-4">
            <h1 className="h3 mb-1">Settings</h1>
            <p className="text-muted">Manage your account settings and preferences.</p>
          </div>

          {message && (
            <div className={`alert ${message.includes('success') ? 'alert-success' : 'alert-danger'} alert-dismissible fade show`} role="alert">
              {message}
              <button type="button" className="btn-close" onClick={() => setMessage("")}></button>
            </div>
          )}

          {/* Profile Settings */}
          <div className="card mb-4">
            <div className="card-header">
              <h5 className="card-title mb-0">Profile Information</h5>
            </div>
            <div className="card-body">
              <form onSubmit={handleProfileSave}>
                <div className="row">
                  <div className="col-md-6">
                    <div className="mb-3">
                      <label className="form-label">Email Address</label>
                      <input
                        type="email"
                        className="form-control"
                        value={profile.email}
                        readOnly
                      />
                      <div className="form-text">Your email address cannot be changed</div>
                    </div>
                  </div>
                  <div className="col-md-6">
                    <div className="mb-3">
                      <label className="form-label">Account Type</label>
                      <input
                        type="text"
                        className="form-control"
                        value={profile.account_type?.charAt(0).toUpperCase() + profile.account_type?.slice(1) || 'Personal'}
                        readOnly
                      />
                    </div>
                  </div>
                </div>

                <div className="row">
                  <div className="col-md-6">
                    <div className="mb-3">
                      <label className="form-label">First Name</label>
                      <input
                        type="text"
                        className="form-control"
                        value={profile.first_name || ""}
                        onChange={(e) => setProfile({...profile, first_name: e.target.value})}
                        placeholder="Enter your first name"
                      />
                    </div>
                  </div>
                  <div className="col-md-6">
                    <div className="mb-3">
                      <label className="form-label">Last Name</label>
                      <input
                        type="text"
                        className="form-control"
                        value={profile.last_name || ""}
                        onChange={(e) => setProfile({...profile, last_name: e.target.value})}
                        placeholder="Enter your last name"
                      />
                    </div>
                  </div>
                </div>

                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={saving}
                >
                  {saving ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                      Saving...
                    </>
                  ) : (
                    'Save Changes'
                  )}
                </button>
              </form>
            </div>
          </div>

          {/* Account Settings */}
          <div className="card">
            <div className="card-header">
              <h5 className="card-title mb-0">Account Settings</h5>
            </div>
            <div className="card-body">
              <div className="d-grid gap-2">
                <button type="button" className="btn btn-outline-primary">
                  Change Password
                </button>
                {profile.account_type === 'personal' && (
                  <button type="button" className="btn btn-success">
                    Upgrade to Business
                  </button>
                )}
                <button type="button" className="btn btn-outline-warning">
                  Export Data
                </button>
                <button type="button" className="btn btn-outline-danger">
                  Delete Account
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
