import { Link, NavLink } from "react-router-dom";

export default function PublicNavbar() {
  return (
    <nav className="navbar navbar-expand-lg" style={{ backgroundColor: '#1a1b1e', borderBottom: '1px solid rgba(255,107,53,0.25)' }}>
      <div className="container">
        <Link className="navbar-brand fw-bold" to="/" style={{ color: '#ff6b35' }}>
          <i className="bi bi-display me-2"></i>
          DisplayAds
        </Link>
        
        <button 
          className="navbar-toggler" 
          type="button" 
          data-bs-toggle="collapse" 
          data-bs-target="#navbarNav"
          aria-controls="navbarNav" 
          aria-expanded="false" 
          aria-label="Toggle navigation"
        >
          <span className="navbar-toggler-icon"></span>
        </button>
        
        <div className="collapse navbar-collapse" id="navbarNav">
          <ul className="navbar-nav me-auto">
            <li className="nav-item">
              <NavLink 
                className={({ isActive }) => 
                  `nav-link ${isActive ? 'fw-semibold' : ''}`
                } 
                to="/features"
                style={({ isActive }) => ({ color: isActive ? '#ff6b35' : '#cbd5e0' })}
              >
                Features
              </NavLink>
            </li>
            <li className="nav-item">
              <NavLink 
                className={({ isActive }) => 
                  `nav-link ${isActive ? 'fw-semibold' : ''}`
                } 
                to="/pricing"
                style={({ isActive }) => ({ color: isActive ? '#ff6b35' : '#cbd5e0' })}
              >
                Pricing
              </NavLink>
            </li>
          </ul>
          
          <div className="d-flex gap-2">
            <Link to="/login" className="btn btn-outline-light" style={{ borderColor: '#ff6b35', color: '#ff6b35' }}>
              Log in
            </Link>
            <Link to="/register" className="btn" style={{ backgroundColor: '#ff6b35', color: '#1a1b1e' }}>
              Get started
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
}
