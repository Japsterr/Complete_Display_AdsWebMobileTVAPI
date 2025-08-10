import { Link } from "react-router-dom";

export default function Footer() {
  return (
    <footer className="text-light py-5 mt-auto" style={{ backgroundColor: '#1a1b1e', borderTop: '1px solid rgba(255,107,53,0.25)' }}>
      <div className="container">
        <div className="row g-4">
          <div className="col-lg-6 col-md-12">
            <div className="d-flex align-items-center mb-3">
              <i className="bi bi-display me-2" style={{fontSize: '1.5rem', color: '#ff6b35'}}></i>
              <span className="h4 mb-0 fw-bold" style={{ color: '#ffd6c5' }}>DisplayAds</span>
            </div>
            <p className="text-light opacity-75">
              The complete digital signage platform for businesses of all sizes. 
              Manage, schedule, and display content across your entire network.
            </p>
          </div>
          
          <div className="col-lg-3 col-md-6">
            <h5 className="text-uppercase fw-bold mb-3 text-light">Product</h5>
            <ul className="list-unstyled">
              <li className="mb-2">
                <Link to="/features" className="text-decoration-none text-light opacity-75 link-light">
                  <i className="bi bi-arrow-right me-2"></i>Features
                </Link>
              </li>
              <li className="mb-2">
                <Link to="/pricing" className="text-decoration-none text-light opacity-75 link-light">
                  <i className="bi bi-arrow-right me-2"></i>Pricing
                </Link>
              </li>
            </ul>
          </div>

          <div className="col-lg-3 col-md-6">
            <h5 className="text-uppercase fw-bold mb-3 text-light">Support</h5>
            <ul className="list-unstyled">
              <li className="mb-2">
                <Link to="/contact" className="text-decoration-none text-light opacity-75 link-light">
                  <i className="bi bi-envelope me-2"></i>Contact
                </Link>
              </li>
              <li className="mb-2">
                <Link to="/documentation" className="text-decoration-none text-light opacity-75 link-light">
                  <i className="bi bi-book me-2"></i>Documentation
                </Link>
              </li>
            </ul>
          </div>
        </div>
        
        <hr className="my-4 border-light opacity-25" />
        
        <div className="row align-items-center">
          <div className="col-md-6">
            <p className="text-light opacity-75 mb-0">
              © 2025 DisplayAds. All rights reserved.
            </p>
          </div>
          <div className="col-md-6 text-md-end">
            <div className="d-flex justify-content-md-end gap-3">
              <a href="#" className="text-light opacity-75 link-light">
                <i className="bi bi-twitter" style={{fontSize: '1.2rem'}}></i>
              </a>
              <a href="#" className="text-light opacity-75 link-light">
                <i className="bi bi-linkedin" style={{fontSize: '1.2rem'}}></i>
              </a>
              <a href="#" className="text-light opacity-75 link-light">
                <i className="bi bi-github" style={{fontSize: '1.2rem'}}></i>
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
