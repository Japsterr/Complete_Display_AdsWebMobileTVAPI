import { useState, useEffect } from "react";
import { UserIcon, BuildingOfficeIcon, StarIcon, CheckIcon } from "@heroicons/react/24/outline";
import api from "../services/api";
import stripeService from "../services/stripe";

interface UserProfile {
  id: number;
  email: string;
  account_type: string;
  first_name?: string;
  last_name?: string;
  date_joined?: string;
}

export default function ProfilePage() {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [saving, setSaving] = useState(false);
  const [upgrading, setUpgrading] = useState(false);
  const [formData, setFormData] = useState({
    first_name: "",
    last_name: "",
  });

  useEffect(() => {
    fetchProfile();
    
    // Check for upgrade success/failure in URL params
    const urlParams = new URLSearchParams(window.location.search);
    const upgradeStatus = urlParams.get('status');
    const upgradePlan = urlParams.get('upgrade');
    
    if (upgradeStatus === 'success' && upgradePlan) {
      const planName = upgradePlan.charAt(0).toUpperCase() + upgradePlan.slice(1);
      showAlert(`Success! Your account has been upgraded to ${planName}. Welcome!`, 'success');
      // Clean up URL
      window.history.replaceState({}, document.title, window.location.pathname);
      // Refresh profile to show updated account type
      setTimeout(() => fetchProfile(), 1000);
    } else if (upgradeStatus === 'cancelled' && upgradePlan) {
      const planName = upgradePlan.charAt(0).toUpperCase() + upgradePlan.slice(1);
      showAlert(`${planName} upgrade cancelled. No charges have been made.`, 'info');
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  const showAlert = (message: string, type: 'success' | 'error' | 'info' = 'success') => {
    const alertClass = type === 'success' ? 'alert-success' : type === 'error' ? 'alert-danger' : 'alert-info';
    const alert = document.createElement('div');
    alert.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
    alert.style.top = '20px';
    alert.style.right = '20px';
    alert.style.zIndex = '9999';
    alert.style.minWidth = '300px';
    alert.innerHTML = `
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alert);
    setTimeout(() => alert.remove(), 5000);
  };

  const handleUpgrade = async (planType: 'business' | 'enterprise') => {
    setUpgrading(true);
    try {
      // Check if user can upgrade to this plan
      const canUpgrade = await stripeService.canUpgrade(planType);
      if (!canUpgrade) {
        const planName = planType.charAt(0).toUpperCase() + planType.slice(1);
        showAlert(`You cannot upgrade to ${planName} plan from your current plan.`, 'info');
        return;
      }

      // Create checkout session and redirect to Stripe
      await stripeService.createCheckoutSession(planType);
      
    } catch (error: any) {
      console.error('Upgrade error:', error);
      showAlert(error.message || 'Failed to start upgrade process. Please try again.', 'error');
    } finally {
      setUpgrading(false);
    }
  };

  const fetchProfile = async () => {
    try {
      const response = await api.get("/auth/profile/");
      setProfile(response.data);
      setFormData({
        first_name: response.data.first_name || "",
        last_name: response.data.last_name || "",
      });
    } catch (error) {
      console.error("Error fetching profile:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      const response = await api.patch("/auth/profile/", formData);
      setProfile(response.data);
      setEditing(false);
      // Show success message
      const successAlert = document.createElement('div');
      successAlert.className = 'alert alert-success alert-dismissible fade show position-fixed';
      successAlert.style.top = '20px';
      successAlert.style.right = '20px';
      successAlert.style.zIndex = '9999';
      successAlert.innerHTML = `
        <strong>Success!</strong> Your profile has been updated.
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
      `;
      document.body.appendChild(successAlert);
      setTimeout(() => successAlert.remove(), 3000);
    } catch (error) {
      console.error("Error updating profile:", error);
      // Show error message
      const errorAlert = document.createElement('div');
      errorAlert.className = 'alert alert-danger alert-dismissible fade show position-fixed';
      errorAlert.style.top = '20px';
      errorAlert.style.right = '20px';
      errorAlert.style.zIndex = '9999';
      errorAlert.innerHTML = `
        <strong>Error!</strong> Failed to update profile. Please try again.
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
      `;
      document.body.appendChild(errorAlert);
      setTimeout(() => errorAlert.remove(), 3000);
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
          <div className="d-flex justify-content-between align-items-center mb-4">
            <h1 className="h3 mb-0">Profile Settings</h1>
            <button
              className="btn btn-outline-primary"
              onClick={() => setEditing(!editing)}
              disabled={saving}
            >
              {editing ? "Cancel" : "Edit Profile"}
            </button>
          </div>

          {/* Account Status Card */}
          <div className="card mb-4">
            <div className="card-header">
              <h5 className="card-title mb-0 d-flex align-items-center">
                {profile?.account_type === "business" ? (
                  <BuildingOfficeIcon className="me-2" style={{ width: "20px", height: "20px" }} />
                ) : (
                  <UserIcon className="me-2" style={{ width: "20px", height: "20px" }} />
                )}
                Account Information
              </h5>
            </div>
            <div className="card-body">
              <div className="row">
                <div className="col-md-6">
                  <div className="d-flex align-items-center justify-content-between">
                    <div>
                      <h6 className="mb-1">
                        {profile?.account_type === "free" && "Free Account"}
                        {profile?.account_type === "business" && "Business Account"}  
                        {profile?.account_type === "enterprise" && "Enterprise Account"}
                      </h6>
                      <p className="text-muted mb-0">
                        {profile?.account_type === "free" && "Basic features with limited usage"}
                        {profile?.account_type === "business" && "Advanced features for small teams"}
                        {profile?.account_type === "enterprise" && "Full enterprise features with unlimited usage"}
                      </p>
                    </div>
                    {profile?.account_type === "free" && (
                      <div className="d-flex gap-2">
                        <button 
                          className="btn btn-success btn-sm"
                          onClick={() => handleUpgrade('business')}
                          disabled={upgrading}
                        >
                          {upgrading ? (
                            <>
                              <span className="spinner-border spinner-border-sm me-1" role="status"></span>
                              Processing...
                            </>
                          ) : (
                            <>
                              <StarIcon style={{ width: "16px", height: "16px" }} className="me-1" />
                              Upgrade to Business
                            </>
                          )}
                        </button>
                        <button 
                          className="btn btn-primary btn-sm"
                          onClick={() => handleUpgrade('enterprise')}
                          disabled={upgrading}
                        >
                          {upgrading ? (
                            <>
                              <span className="spinner-border spinner-border-sm me-1" role="status"></span>
                              Processing...
                            </>
                          ) : (
                            <>
                              <StarIcon style={{ width: "16px", height: "16px" }} className="me-1" />
                              Upgrade to Enterprise
                            </>
                          )}
                        </button>
                      </div>
                    )}
                    {profile?.account_type === "business" && (
                      <button 
                        className="btn btn-primary btn-sm"
                        onClick={() => handleUpgrade('enterprise')}
                        disabled={upgrading}
                      >
                        {upgrading ? (
                          <>
                            <span className="spinner-border spinner-border-sm me-1" role="status"></span>
                            Processing...
                          </>
                        ) : (
                          <>
                            <StarIcon style={{ width: "16px", height: "16px" }} className="me-1" />
                            Upgrade to Enterprise
                          </>
                        )}
                      </button>
                    )}
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="text-md-end">
                    <small className="text-muted">
                      Member since: {profile?.date_joined ? new Date(profile.date_joined).toLocaleDateString() : 'N/A'}
                    </small>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Business Features Card (for business accounts) */}
          {profile?.account_type === "business" && (
            <div className="card mb-4">
              <div className="card-header">
                <h5 className="card-title mb-0 d-flex align-items-center">
                  <BuildingOfficeIcon className="me-2" style={{ width: "20px", height: "20px" }} />
                  Business Features
                </h5>
              </div>
              <div className="card-body">
                <div className="row g-3">
                  <div className="col-sm-6 col-lg-3">
                    <div className="d-flex align-items-center">
                      <CheckIcon style={{ width: "16px", height: "16px" }} className="text-success me-2" />
                      <span className="small">Team Collaboration</span>
                    </div>
                  </div>
                  <div className="col-sm-6 col-lg-3">
                    <div className="d-flex align-items-center">
                      <CheckIcon style={{ width: "16px", height: "16px" }} className="text-success me-2" />
                      <span className="small">Advanced Analytics</span>
                    </div>
                  </div>
                  <div className="col-sm-6 col-lg-3">
                    <div className="d-flex align-items-center">
                      <CheckIcon style={{ width: "16px", height: "16px" }} className="text-success me-2" />
                      <span className="small">Priority Support</span>
                    </div>
                  </div>
                  <div className="col-sm-6 col-lg-3">
                    <div className="d-flex align-items-center">
                      <CheckIcon style={{ width: "16px", height: "16px" }} className="text-success me-2" />
                      <span className="small">API Access</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Profile Information Card */}
          <div className="card">
            <div className="card-header">
              <h5 className="card-title mb-0">Profile Information</h5>
            </div>
            <div className="card-body">
              <div className="row">
                <div className="col-md-6">
                  <div className="mb-3">
                    <label className="form-label">Email Address</label>
                    <input
                      type="email"
                      className="form-control"
                      value={profile?.email || ""}
                      readOnly
                    />
                    <div className="form-text">Your email address cannot be changed</div>
                  </div>
                </div>
                <div className="col-md-6">
                  <div className="mb-3">
                    <label className="form-label">Account ID</label>
                    <input
                      type="text"
                      className="form-control"
                      value={profile?.id || ""}
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
                      value={formData.first_name}
                      onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                      readOnly={!editing}
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
                      value={formData.last_name}
                      onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                      readOnly={!editing}
                      placeholder="Enter your last name"
                    />
                  </div>
                </div>
              </div>

              {editing && (
                <div className="d-flex gap-2">
                  <button
                    type="button"
                    className="btn btn-primary"
                    onClick={handleSave}
                    disabled={saving}
                  >
                    {saving ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                        Saving...
                      </>
                    ) : (
                      "Save Changes"
                    )}
                  </button>
                  <button
                    type="button"
                    className="btn btn-outline-secondary"
                    onClick={() => setEditing(false)}
                    disabled={saving}
                  >
                    Cancel
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Account Actions Card */}
          <div className="card mt-4">
            <div className="card-header">
              <h5 className="card-title mb-0">Account Actions</h5>
            </div>
            <div className="card-body">
              <div className="row g-3">
                {profile?.account_type === "free" && (
                  <>
                    <div className="col-md-6">
                      <button 
                        className="btn btn-success w-100"
                        onClick={() => handleUpgrade('business')}
                        disabled={upgrading}
                      >
                        {upgrading ? (
                          <>
                            <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                            Processing...
                          </>
                        ) : (
                          <>
                            <StarIcon style={{ width: "16px", height: "16px" }} className="me-2" />
                            Upgrade to Business - R99/month
                          </>
                        )}
                      </button>
                    </div>
                    <div className="col-md-6">
                      <button 
                        className="btn btn-primary w-100"
                        onClick={() => handleUpgrade('enterprise')}
                        disabled={upgrading}
                      >
                        {upgrading ? (
                          <>
                            <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                            Processing...
                          </>
                        ) : (
                          <>
                            <StarIcon style={{ width: "16px", height: "16px" }} className="me-2" />
                            Upgrade to Enterprise - R500/month
                          </>
                        )}
                      </button>
                    </div>
                  </>
                )}
                {profile?.account_type === "business" && (
                  <div className="col-md-6">
                    <button 
                      className="btn btn-primary w-100"
                      onClick={() => handleUpgrade('enterprise')}
                      disabled={upgrading}
                    >
                      {upgrading ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                          Processing...
                        </>
                      ) : (
                        <>
                          <StarIcon style={{ width: "16px", height: "16px" }} className="me-2" />
                          Upgrade to Enterprise - R500/month
                        </>
                      )}
                    </button>
                  </div>
                )}
                {profile?.account_type === "enterprise" && (
                  <div className="col-12">
                    <div className="alert alert-success" role="alert">
                      <StarIcon style={{ width: "20px", height: "20px" }} className="me-2" />
                      You're on the Enterprise plan with full access to all features!
                    </div>
                  </div>
                )}
                <div className="col-md-6">
                  <button className="btn btn-outline-primary w-100">
                    Change Password
                  </button>
                </div>
                <div className="col-md-6">
                  <button className="btn btn-outline-secondary w-100">
                    Download Data
                  </button>
                </div>
                <div className="col-md-6">
                  <button className="btn btn-outline-danger w-100">
                    Delete Account
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
