import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import api from "../services/api";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    
    try {
      // Try the SimpleJWT endpoint first for testing
      const res = await api.post("/login-simple/", { email, password });
      localStorage.setItem("access_token", res.data.access);
      localStorage.setItem("refresh_token", res.data.refresh);
      navigate("/dashboard");
    } catch (err: any) {
      console.error("Login error:", err);
      setError(err.response?.data?.detail || "Invalid credentials. Please try again.");
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
                    Welcome Back to DisplayAds
                  </h2>
                  <p className="text-secondary">
                    Sign in to manage your digital signage campaigns
                  </p>
                </div>

                {error && (
                  <div className="alert alert-danger d-flex align-items-center" role="alert">
                    <div>
                      <strong>Sign In Failed:</strong> {error}
                    </div>
                  </div>
                )}

                <form onSubmit={handleSubmit}>
                  <div className="mb-3">
                    <label htmlFor="email" className="form-label">
                      Email Address
                    </label>
                    <input
                      id="email"
                      name="email"
                      type="email"
                      required
                      className="form-control"
                      placeholder="Enter your email"
                      autoComplete="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                    />
                  </div>

                  <div className="mb-4">
                    <label htmlFor="password" className="form-label">
                      Password
                    </label>
                    <input
                      id="password"
                      name="password"
                      type="password"
                      required
                      className="form-control"
                      placeholder="Enter your password"
                      autoComplete="current-password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                    />
                  </div>

                  <button 
                    type="submit" 
                    className="btn btn-primary w-100 py-3 fw-semibold"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                        Signing in...
                      </>
                    ) : (
                      <>
                        🚀 Sign In
                      </>
                    )}
                  </button>
                </form>

                {/* Sign Up Link */}
                <div className="text-center mt-4">
                  <p className="text-secondary mb-0">
                    Don't have an account?{' '}
                    <Link
                      to="/register"
                      className="text-primary fw-semibold text-decoration-none"
                    >
                      Create account here
                    </Link>
                  </p>
                </div>

                {/* Quick Features */}
                <div className="mt-4 pt-4 border-top">
                  <div className="row text-center g-3">
                    <div className="col-4">
                      <div className="text-primary mb-1">📱</div>
                      <small className="text-secondary">QR Activation</small>
                    </div>
                    <div className="col-4">
                      <div className="text-primary mb-1">📊</div>
                      <small className="text-secondary">Real-time Analytics</small>
                    </div>
                    <div className="col-4">
                      <div className="text-primary mb-1">🌐</div>
                      <small className="text-secondary">Cloud Dashboard</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Security Info */}
            <div className="text-center mt-4">
              <p className="text-secondary mb-0">
                <small>🔒 Secure login • 🌍 Access from anywhere • 📱 Mobile optimized</small>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}