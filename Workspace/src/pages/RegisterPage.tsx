import React from "react";
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../services/api.ts";

export default function RegisterPage() {
  const [form, setForm] = useState({
    email: "",
    password: "",
    firstName: "",
    lastName: "",
    accountType: "personal",
    businessName: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    
    try {
      const payload = {
        email: form.email,
        password: form.password,
        first_name: form.firstName,
        last_name: form.lastName,
        account_type: form.accountType,
        ...(form.accountType === "business" && { business_name: form.businessName }),
      };
      
      console.log("Registration payload:", payload);
      
      const res = await api.post("/auth/register/", payload);
      
      if (res.data.access && res.data.refresh) {
        localStorage.setItem("access_token", res.data.access);
        localStorage.setItem("refresh_token", res.data.refresh);
        navigate("/dashboard");
      } else {
        setError("Registration completed but login failed. Please try signing in.");
      }
    } catch (err: any) {
      console.error("Registration error:", err);
      
      if (err.response?.data?.details) {
        // Handle specific field errors
        const details = err.response.data.details;
        let errorMessage = "Please fix the following issues:\n";
        
        Object.keys(details).forEach(field => {
          const fieldErrors = Array.isArray(details[field]) ? details[field] : [details[field]];
          errorMessage += `• ${field}: ${fieldErrors.join(", ")}\n`;
        });
        
        setError(errorMessage);
      } else if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else if (err.response?.data?.message) {
        setError(err.response.data.message);
      } else if (err.message) {
        setError(`Network error: ${err.message}`);
      } else {
        setError("Registration failed. Please check your details and try again.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-vh-100 d-flex align-items-center" style={{background: 'var(--bg-primary)'}}>
      <div className="container">
        <div className="row justify-content-center">
          <div className="col-md-6 col-lg-5">
            <div className="card shadow-lg border-0" style={{borderRadius: 'var(--radius-xl)'}}>
              <div className="card-body p-5">
                {/* Header */}
                <div className="text-center mb-4">
                  <div className="mb-3">
                    <div className="feature-icon mx-auto" style={{width: '80px', height: '80px'}}>
                      📱
                    </div>
                  </div>
                  <h2 className="fw-bold text-primary mb-3">
                    Create Your DisplayAds Account
                  </h2>
                  <p className="text-secondary">
                    Join the mobile-first digital signage revolution
                  </p>
                </div>

                {/* Account Type Selection */}
                <div className="mb-4">
                  <label className="form-label fw-semibold">Account Type</label>
                  <div className="row g-2">
                    {["personal", "business"].map(type => (
                      <div key={type} className="col-6">
                        <button
                          type="button"
                          className={`btn w-100 ${
                            form.accountType === type
                              ? "btn-primary"
                              : "btn-outline-secondary"
                          }`}
                          onClick={() => setForm(f => ({ ...f, accountType: type }))}
                        >
                          {type === "personal" ? "👤 Personal" : "🏢 Business"}
                        </button>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Registration Form */}
                <form onSubmit={handleSubmit}>
                  <div className="row g-3">
                    <div className="col-md-6">
                      <label htmlFor="firstName" className="form-label">
                        First Name
                      </label>
                      <input
                        id="firstName"
                        name="firstName"
                        type="text"
                        className="form-control"
                        placeholder="Enter first name"
                        autoComplete="given-name"
                        required
                        value={form.firstName}
                        onChange={e => setForm(f => ({ ...f, firstName: e.target.value }))}
                      />
                    </div>
                    <div className="col-md-6">
                      <label htmlFor="lastName" className="form-label">
                        Last Name
                      </label>
                      <input
                        id="lastName"
                        name="lastName"
                        type="text"
                        className="form-control"
                        placeholder="Enter last name"
                        autoComplete="family-name"
                        required
                        value={form.lastName}
                        onChange={e => setForm(f => ({ ...f, lastName: e.target.value }))}
                      />
                    </div>
                  </div>

                  <div className="mb-3">
                    <label htmlFor="email" className="form-label">
                      Email Address
                    </label>
                    <input
                      id="email"
                      name="email"
                      type="email"
                      className="form-control"
                      placeholder="Enter your email"
                      autoComplete="email"
                      required
                      value={form.email}
                      onChange={e => setForm(f => ({ ...f, email: e.target.value }))}
                    />
                  </div>

                  <div className="mb-3">
                    <label htmlFor="password" className="form-label">
                      Password
                    </label>
                    <input
                      id="password"
                      name="password"
                      type="password"
                      className="form-control"
                      placeholder="Create a secure password"
                      autoComplete="new-password"
                      required
                      value={form.password}
                      onChange={e => setForm(f => ({ ...f, password: e.target.value }))}
                    />
                  </div>

                  {form.accountType === "business" && (
                    <div className="mb-3">
                      <label htmlFor="businessName" className="form-label">
                        Business Name
                      </label>
                      <input
                        id="businessName"
                        name="businessName"
                        type="text"
                        className="form-control"
                        placeholder="Enter your business name"
                        autoComplete="organization"
                        required
                        value={form.businessName}
                        onChange={e => setForm(f => ({ ...f, businessName: e.target.value }))}
                      />
                    </div>
                  )}

                  {error && (
                    <div className="alert alert-danger d-flex align-items-center" role="alert">
                      <div>
                        <strong>Registration Failed:</strong> {error}
                      </div>
                    </div>
                  )}

                  <button
                    type="submit"
                    className="btn btn-primary w-100 py-3 fw-semibold"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                        Creating Account...
                      </>
                    ) : (
                      <>
                        🚀 Create Account
                      </>
                    )}
                  </button>
                </form>

                {/* Sign In Link */}
                <div className="text-center mt-4">
                  <p className="text-secondary mb-0">
                    Already have an account?{' '}
                    <Link
                      to="/login"
                      className="text-primary fw-semibold text-decoration-none"
                    >
                      Sign in here
                    </Link>
                  </p>
                </div>

                {/* Features Preview */}
                <div className="mt-4 pt-4 border-top">
                  <div className="row text-center g-3">
                    <div className="col-4">
                      <div className="text-primary mb-1">📱</div>
                      <small className="text-secondary">QR Activation</small>
                    </div>
                    <div className="col-4">
                      <div className="text-primary mb-1">📊</div>
                      <small className="text-secondary">Analytics</small>
                    </div>
                    <div className="col-4">
                      <div className="text-primary mb-1">🌐</div>
                      <small className="text-secondary">Multi-Platform</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Additional Info */}
            <div className="text-center mt-4">
              <p className="text-secondary mb-0">
                <small>🔒 Your data is secure • 🆓 Free forever plan available • ❌ No credit card required</small>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
