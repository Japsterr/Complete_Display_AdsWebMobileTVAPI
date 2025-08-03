import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { 
  ChevronDownIcon, 
  UserCircleIcon, 
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  MagnifyingGlassIcon
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

  const displayName = user ? 
    (user.first_name && user.last_name ? `${user.first_name} ${user.last_name}` : user.email) 
    : 'Loading...';

  return (
    <header className="header-main bg-white border-bottom py-3">
      <div className="container-fluid">
        <div className="d-flex align-items-center justify-content-between">
          {/* Mobile menu button */}
          <div className="d-md-none">
            <button
              type="button"
              className="btn btn-outline-secondary btn-sm"
              onClick={onMenuClick}
            >
              <Bars3Icon style={{ width: "20px", height: "20px" }} />
            </button>
          </div>

          {/* Search */}
          <div className="flex-grow-1 d-flex justify-content-center px-2">
            <div className="position-relative" style={{ maxWidth: "400px", width: "100%" }}>
              <div className="position-absolute top-50 start-0 translate-middle-y ps-3">
                <MagnifyingGlassIcon style={{ width: "16px", height: "16px" }} className="text-muted" />
              </div>
              <input
                type="search"
                className="form-control ps-5"
                placeholder="Search..."
                style={{ paddingLeft: "2.5rem" }}
              />
            </div>
          </div>

          {/* Profile dropdown */}
          <div className="ms-3">
            <div className="dropdown">
              <button
                type="button"
                className="btn btn-link text-decoration-none d-flex align-items-center"
                onClick={() => setUserMenuOpen(!userMenuOpen)}
              >
                <UserCircleIcon style={{ width: "32px", height: "32px" }} className="text-muted me-2" />
                <div className="d-none d-md-block text-start me-2">
                  <div className="fw-medium text-dark" style={{ fontSize: "0.875rem" }}>
                    {displayName}
                  </div>
                  {user && (
                    <div className="text-muted" style={{ fontSize: "0.75rem" }}>
                      {user.email}
                    </div>
                  )}
                </div>
                <ChevronDownIcon style={{ width: "16px", height: "16px" }} className="text-muted" />
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
