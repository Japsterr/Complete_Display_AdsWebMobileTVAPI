import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { 
  ChevronDownIcon, 
  UserCircleIcon, 
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  TvIcon
} from "@heroicons/react/24/outline";
import api from "../services/api";

interface HeaderProps {
  onMenuClick?: () => void;
}

interface UserProfile {
  id: number;
  email: string;
  first_name?: string;
  last_name?: string;
  account_type: string;
}

export default function Header({ onMenuClick }: HeaderProps) {
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [user, setUser] = useState<UserProfile | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchUserProfile();
  }, []);

  async function fetchUserProfile() {
    try {
      const response = await api.get('/auth/profile/');
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user profile:', error);
      // Fallback to default if API fails
      setUser({
        id: 0,
        email: 'user@example.com',
        first_name: 'User',
        last_name: '',
        account_type: 'personal'
      });
    }
  }

  function handleLogout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    navigate("/login");
  }

  function handleLogoClick() {
    navigate("/dashboard");
  }

  const displayName = user ? 
    (user.first_name && user.last_name ? `${user.first_name} ${user.last_name}` : user.email) 
    : 'Loading...';

  return (
    <header className="header-main py-3 shadow-sm" style={{ backgroundColor: '#1a1b1e', borderBottom: '1px solid rgba(255,107,53,0.25)' }}>
      <div className="container-fluid">
        <div className="d-flex align-items-center justify-content-between">
          {/* Left: Mobile menu + Logo */}
          <div className="d-flex align-items-center">
            {/* Mobile menu button */}
            <div className="d-md-none me-3">
              <button
                type="button"
                className="btn btn-outline-light btn-sm"
                onClick={onMenuClick}
              >
                <Bars3Icon style={{ width: "20px", height: "20px" }} />
              </button>
            </div>

            {/* Logo/Brand */}
            <button
              type="button"
              className="btn btn-link text-decoration-none p-0 d-flex align-items-center"
              onClick={handleLogoClick}
            >
              <div className="d-flex align-items-center">
                <div className="rounded-circle p-2 me-3 shadow-sm" style={{ background: 'linear-gradient(135deg, #ff6b35 0%, #ff925f 100%)' }}>
                  <TvIcon style={{ width: "24px", height: "24px", color: '#1a1b1e' }} />
                </div>
                <div className="text-white">
                  <div className="fw-bold" style={{ fontSize: "1.25rem", lineHeight: "1.2" }}>
                    Digital Signage
                  </div>
                  <div style={{ fontSize: "0.75rem", opacity: "0.9" }}>
                    Platform
                  </div>
                </div>
              </div>
            </button>
          </div>

          {/* Right: Profile dropdown */}
          <div className="ms-3">
            <div className="dropdown">
              <button
                type="button"
                className="btn btn-outline-light text-decoration-none d-flex align-items-center px-3 py-2"
                onClick={() => setUserMenuOpen(!userMenuOpen)}
              >
                <UserCircleIcon style={{ width: "32px", height: "32px" }} className="text-white me-2" />
                <div className="d-none d-md-block text-start me-2">
                  <div className="fw-medium text-white" style={{ fontSize: "0.875rem" }}>
                    {displayName}
                  </div>
                  {user && (
                    <div className="text-white-50" style={{ fontSize: "0.75rem" }}>
                      {user.email}
                    </div>
                  )}
                </div>
                <ChevronDownIcon style={{ width: "16px", height: "16px" }} className="text-white" />
              </button>
              {userMenuOpen && (
                <div className="dropdown-menu dropdown-menu-end show position-absolute" style={{ zIndex: 1050 }}>
                  <button
                    className="dropdown-item d-flex align-items-center"
                    onClick={handleLogout}
                  >
                    <ArrowRightOnRectangleIcon style={{ width: "16px", height: "16px" }} className="me-2" />
                    Sign out
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
