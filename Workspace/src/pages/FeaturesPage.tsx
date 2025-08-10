import React from 'react';

const FeaturesPage: React.FC = () => {
  const features = [
    {
      icon: '📱',
      title: 'QR Code TV Activation',
      description: 'Revolutionary mobile QR scanning to instantly activate TV displays. Point, scan, done!',
      highlight: 'Industry First',
      gradient: 'qr-highlight'
    },
    {
      icon: '🌐',
      title: 'Professional Web Dashboard',
      description: 'Complete campaign management, media library, analytics, and team collaboration in one place.',
      highlight: 'Full-Featured'
    },
    {
      icon: '📊',
      title: 'Real-Time Analytics',
      description: 'Device heartbeats, media impressions, campaign performance, and detailed reporting.',
      highlight: 'Live Data'
    },
    {
      icon: '🎬',
      title: 'Visual Campaign Builder',
      description: 'Drag-and-drop playlist creator with scheduling, priorities, and automatic fallbacks.',
      highlight: 'Intuitive'
    },
    {
      icon: '📁',
      title: 'Smart Media Library',
      description: 'Upload images & videos, organize by categories, with mobile camera integration.',
      highlight: 'Organized'
    },
    {
      icon: '📺',
      title: 'Display Management',
      description: 'Monitor device status, assign campaigns, track performance across multiple locations.',
      highlight: 'Scalable'
    },
    {
      icon: '👥',
      title: 'Team Collaboration',
      description: 'Multi-user business accounts with role-based permissions (Owner, Admin, Editor, Viewer).',
      highlight: 'Business Ready'
    },
    {
      icon: '💳',
      title: 'Stripe Payment Integration',
      description: 'Automated billing, subscription management, South African Rand (ZAR) support.',
      highlight: 'Local Currency'
    },
    {
      icon: '📱',
      title: 'Native Mobile App',
      description: 'React Native app for iOS & Android with camera integration and offline capabilities.',
      highlight: 'Cross-Platform'
    },
    {
      icon: '🔄',
      title: 'Automatic Scheduling',
      description: 'Smart campaign scheduling with priorities, recurring schedules, and conflict detection.',
      highlight: 'Intelligent'
    },
    {
      icon: '🔐',
      title: 'Enterprise Security',
      description: 'JWT authentication, role-based access, HTTPS encryption, and data protection.',
      highlight: 'Secure'
    },
    {
      icon: '⚡',
      title: 'Real-Time Updates',
      description: 'Live device monitoring, instant campaign updates, and heartbeat tracking.',
      highlight: 'Instant'
    }
  ];

  const advantages = [
    {
      title: 'Mobile-First Innovation',
      description: 'QR code activation transforms traditional digital signage deployment',
      icon: '🚀'
    },
    {
      title: 'Complete Ecosystem',
      description: 'Web dashboard + Mobile app + TV display app = Total solution',
      icon: '🌟'
    },
    {
      title: 'South African Focus',
      description: 'ZAR currency, local payment processing, timezone support',
      icon: '🇿🇦'
    },
    {
      title: 'Modern Technology',
      description: 'React, React Native, Django REST API, TypeScript, Bootstrap',
      icon: '💻'
    }
  ];

  return (
    <div className="features-page">
      {/* Hero Section */}
  <section className="hero-section text-center">
        <div className="container">
          <div className="row justify-content-center">
            <div className="col-lg-8">
              <div className="mobile-first-badge fade-in">
                🏆 Industry-Leading Mobile-First Digital Signage
              </div>
              <h1 className="hero-title fade-in">
                Revolutionary Digital Signage Features
              </h1>
              <p className="hero-subtitle fade-in">
                Experience the future of digital signage with QR code activation, 
                real-time analytics, and a complete mobile management ecosystem.
              </p>
              <div className="mt-4 fade-in">
                <a href="/register" className="btn btn-primary btn-lg me-3">
                  Start Free Trial
                </a>
                <a href="/pricing" className="btn btn-outline-light btn-lg">
                  View Pricing
                </a>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Core Features Grid */}
  <section className="py-5" style={{ background: '#1a1b1e' }}>
        <div className="container">
          <div className="row text-center mb-5">
            <div className="col-lg-8 mx-auto">
              <h2 className="display-4 fw-bold mb-3" style={{ color: '#ff6b35' }}>
                Powerful Features Built for Success
              </h2>
              <p className="lead" style={{ color: '#a8b0b8' }}>
                Every feature designed to make digital signage management effortless and effective
              </p>
            </div>
          </div>

          <div className="row g-4">
            {features.map((feature, index) => (
              <div key={index} className="col-lg-4 col-md-6">
                <div className="feature-card hover-scale">
                  <div className="feature-icon">
                    {feature.icon}
                  </div>
                  <h4 className="fw-bold mb-3">{feature.title}</h4>
                  {feature.highlight && (
                    <span className={`badge ${feature.gradient || 'bg-primary'} mb-3`}>
                      {feature.highlight}
                    </span>
                  )}
                  <p style={{ color: '#a8b0b8' }}>
                    {feature.description}
                  </p>
                </div>
              </div>
            ))}
          </div>

          {/* QR Code Highlight Section */}
          <div className="row mt-5">
            <div className="col-12">
              <div className="card text-white" style={{background: 'linear-gradient(135deg, rgba(255,107,53,0.2) 0%, rgba(255,146,95,0.2) 100%)', color: '#ffd6c5', border: '1px solid rgba(255,107,53,0.25)'}}>
                <div className="card-body p-5 text-center">
                  <div className="row align-items-center">
                    <div className="col-lg-8">
                      <h3 className="fw-bold mb-3" style={{ color: '#ffd6c5' }}>
                        🎯 Game-Changing QR Code Activation
                      </h3>
                      <p className="lead mb-0" style={{ color: '#ffd6c5' }}>
                        The first digital signage platform where you can activate TV displays 
                        by simply scanning a QR code with your phone. No more manual setup, 
                        no more complicated activation processes.
                      </p>
                    </div>
                    <div className="col-lg-4">
                      <div className="display-1">📱➡️📺</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Competitive Advantages */}
  <section className="py-5" style={{background: '#1e1f22', borderTop: '1px solid rgba(255,107,53,0.12)', borderBottom: '1px solid rgba(255,107,53,0.12)'}}>
        <div className="container">
          <div className="row text-center mb-5">
            <div className="col-lg-8 mx-auto">
              <h2 className="display-4 fw-bold mb-3" style={{ color: '#ff6b35' }}>
                Why Choose DisplayAds?
              </h2>
              <p className="lead" style={{ color: '#a8b0b8' }}>
                Competitive advantages that set us apart in the digital signage market
              </p>
            </div>
          </div>

          <div className="row g-4">
            {advantages.map((advantage, index) => (
              <div key={index} className="col-lg-6">
                <div className="card h-100 hover-shadow" style={{ background: '#222325', border: '1px solid rgba(255,107,53,0.12)' }}>
                  <div className="card-body p-4">
                    <div className="d-flex align-items-start">
                      <div className="feature-icon me-4" style={{width: '60px', height: '60px', fontSize: '1.5rem'}}>
                        {advantage.icon}
                      </div>
                      <div>
                        <h5 className="fw-bold mb-3" style={{ color: '#e6e1e3' }}>{advantage.title}</h5>
                        <p className="mb-0" style={{ color: '#a8b0b8' }}>{advantage.description}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Technical Stack */}
  <section className="py-5" style={{ background: '#1a1b1e' }}>
        <div className="container">
          <div className="row text-center mb-5">
            <div className="col-lg-8 mx-auto">
              <h2 className="display-4 fw-bold mb-3" style={{ color: '#ff6b35' }}>
                Built with Modern Technology
              </h2>
              <p className="lead" style={{ color: '#a8b0b8' }}>
                Enterprise-grade technology stack for reliability and performance
              </p>
            </div>
          </div>

          <div className="row g-4">
            <div className="col-lg-3 col-md-6 text-center">
              <div className="card hover-scale h-100" style={{ background: '#222325', border: '1px solid rgba(255,107,53,0.12)' }}>
                <div className="card-body p-4">
                  <div className="feature-icon mb-3">⚛️</div>
                  <h5 className="fw-bold" style={{ color: '#e6e1e3' }}>React 19.1.0</h5>
                  <p className="mb-0" style={{ color: '#a8b0b8' }}>Modern web dashboard with TypeScript</p>
                </div>
              </div>
            </div>
            <div className="col-lg-3 col-md-6 text-center">
              <div className="card hover-scale h-100" style={{ background: '#222325', border: '1px solid rgba(255,107,53,0.12)' }}>
                <div className="card-body p-4">
                  <div className="feature-icon mb-3">📱</div>
                  <h5 className="fw-bold" style={{ color: '#e6e1e3' }}>React Native</h5>
                  <p className="mb-0" style={{ color: '#a8b0b8' }}>Cross-platform mobile apps</p>
                </div>
              </div>
            </div>
            <div className="col-lg-3 col-md-6 text-center">
              <div className="card hover-scale h-100" style={{ background: '#222325', border: '1px solid rgba(255,107,53,0.12)' }}>
                <div className="card-body p-4">
                  <div className="feature-icon mb-3">🐍</div>
                  <h5 className="fw-bold" style={{ color: '#e6e1e3' }}>Django REST</h5>
                  <p className="mb-0" style={{ color: '#a8b0b8' }}>Robust backend API with PostgreSQL</p>
                </div>
              </div>
            </div>
            <div className="col-lg-3 col-md-6 text-center">
              <div className="card hover-scale h-100" style={{ background: '#222325', border: '1px solid rgba(255,107,53,0.12)' }}>
                <div className="card-body p-4">
                  <div className="feature-icon mb-3">💳</div>
                  <h5 className="fw-bold" style={{ color: '#e6e1e3' }}>Stripe</h5>
                  <p className="mb-0" style={{ color: '#a8b0b8' }}>Secure payment processing</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action */}
  <section className="py-5" style={{background: 'linear-gradient(135deg, rgba(255,107,53,0.2) 0%, rgba(255,146,95,0.15) 100%)', borderTop: '1px solid rgba(255,107,53,0.25)'}}>
        <div className="container">
          <div className="row text-center text-white">
            <div className="col-lg-8 mx-auto">
              <h2 className="display-4 fw-bold mb-3" style={{ color: '#ffd6c5' }}>
                Ready to Transform Your Digital Signage?
              </h2>
              <p className="lead mb-4 opacity-90" style={{ color: '#ffd6c5' }}>
                Join the mobile-first revolution in digital signage. Start with our free plan today 
                and experience the power of QR code activation.
              </p>
              <div className="d-flex justify-content-center gap-3 flex-wrap">
                <a href="/register" className="btn btn-primary btn-lg px-5" style={{ color: '#1a1b1e' }}><strong>Start Free Plan</strong></a>
                <a href="/contact" className="btn btn-outline-light btn-lg px-5">Schedule Demo</a>
              </div>
              <p className="mt-3 opacity-75">
                <small>No credit card required • Free forever plan • Upgrade anytime</small>
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default FeaturesPage;
