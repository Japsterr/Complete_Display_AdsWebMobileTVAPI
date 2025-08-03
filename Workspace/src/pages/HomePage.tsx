import { Link } from "react-router-dom";

const features = [
  {
    icon: "📱",
    title: "QR Code TV Activation",
    desc: "Revolutionary mobile QR scanning to instantly activate and manage TV displays. Point, scan, done!",
    highlight: "Game Changer"
  },
  {
    icon: "🌐",
    title: "Complete Web Dashboard", 
    desc: "Professional campaign management, media library, analytics, and team collaboration in one place.",
    highlight: "Full-Featured"
  },
  {
    icon: "📊",
    title: "Real-Time Analytics",
    desc: "Device heartbeats, media impressions, campaign performance tracking with live data insights.",
    highlight: "Live Data"
  },
  {
    icon: "🎬",
    title: "Visual Campaign Builder",
    desc: "Drag-and-drop playlist creator with scheduling, priorities, and automatic fallback content.",
    highlight: "Intuitive"
  },
  {
    icon: "📱",
    title: "Native Mobile Apps",
    desc: "iOS & Android apps with camera integration, QR scanning, and complete account management.",
    highlight: "Cross-Platform"
  },
  {
    icon: "💳",
    title: "Stripe Integration",
    desc: "Automated billing, subscription management, and South African Rand (ZAR) payment support.",
    highlight: "Local Currency"
  },
];

const stats = [
  { number: "99.9%", label: "Uptime Guarantee" },
  { number: "< 2s", label: "QR Activation Time" },
  { number: "ZAR", label: "Local Currency Support" },
  { number: "24/7", label: "Device Monitoring" },
];

const testimonials = [
  {
    quote: "The QR code activation is revolutionary! Our technicians can set up displays in seconds instead of minutes.",
    author: "Sarah Johnson",
    company: "Digital Displays SA",
    role: "Operations Manager"
  },
  {
    quote: "Having a complete mobile app alongside the web dashboard makes managing our signage network effortless.",
    author: "Mike Chen", 
    company: "Retail Innovation",
    role: "IT Director"
  },
  {
    quote: "South African Rand support and local payment processing made adoption seamless for our business.",
    author: "Priya Patel",
    company: "Cape Town Shopping Centre",
    role: "Marketing Director"
  }
];

export default function HomePage() {
  return (
    <div className="homepage">
      {/* Hero Section */}
      <section className="hero-section text-center">
        <div className="container">
          <div className="row justify-content-center">
            <div className="col-lg-10">
              <div className="mobile-first-badge fade-in">
                🏆 First QR Code-Activated Digital Signage Platform
              </div>
              <h1 className="hero-title fade-in">
                Transform Your Business with{' '}
                <span style={{background: 'var(--secondary-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent'}}>
                  Mobile-First Digital Signage
                </span>
              </h1>
              <p className="hero-subtitle fade-in">
                The world's first digital signage platform where you can activate TV displays 
                by simply scanning a QR code with your phone. Complete ecosystem with web dashboard, 
                mobile apps, and TV display software.
              </p>
              <div className="d-flex gap-3 justify-content-center mb-4 fade-in flex-wrap">
                <Link to="/register" className="btn btn-primary btn-lg px-5">
                  <strong>Start Free Trial</strong>
                </Link>
                <Link to="/features" className="btn btn-outline-light btn-lg px-5">
                  See All Features
                </Link>
              </div>
              <p className="text-white opacity-75">
                <small>🇿🇦 Built for South Africa • ZAR Currency • No Setup Fees</small>
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-4" style={{background: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(10px)'}}>
        <div className="container">
          <div className="row text-center">
            {stats.map((stat, index) => (
              <div key={index} className="col-6 col-lg-3 mb-3 mb-lg-0">
                <h3 className="fw-bold text-primary mb-1" style={{fontSize: '2rem'}}>
                  {stat.number}
                </h3>
                <p className="text-secondary mb-0 fw-medium">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Overview */}
      <section className="py-5" style={{background: 'var(--bg-primary)'}}>
        <div className="container">
          <div className="text-center mb-5">
            <h2 className="display-4 fw-bold mb-3 text-primary">
              Revolutionary Features That Set Us Apart
            </h2>
            <p className="lead text-secondary">
              Every feature designed to make digital signage management effortless and effective
            </p>
          </div>
          <div className="row g-4">
            {features.map((feature, index) => (
              <div key={index} className="col-lg-4 col-md-6">
                <div className="feature-card hover-scale">
                  <div className="feature-icon">
                    {feature.icon}
                  </div>
                  <h4 className="fw-bold mb-3">{feature.title}</h4>
                  <span className="badge bg-primary mb-3">{feature.highlight}</span>
                  <p className="text-secondary">
                    {feature.desc}
                  </p>
                </div>
              </div>
            ))}
          </div>

          {/* QR Code Demo Section */}
          <div className="row mt-5">
            <div className="col-12">
              <div className="card text-center" style={{background: 'var(--secondary-gradient)', color: 'white', border: 'none'}}>
                <div className="card-body p-5">
                  <div className="row align-items-center">
                    <div className="col-lg-8">
                      <h3 className="fw-bold mb-3">
                        🎯 See QR Code Activation in Action
                      </h3>
                      <p className="lead mb-4">
                        Watch how easy it is to activate a TV display in under 2 seconds. 
                        No manual setup, no complicated configurations - just point and scan!
                      </p>
                      <Link to="/features" className="btn btn-light btn-lg">
                        Learn More About QR Activation
                      </Link>
                    </div>
                    <div className="col-lg-4">
                      <div className="display-1 animate-pulse">📱➡️📺</div>
                      <p className="mb-0 opacity-90">
                        <small>Mobile App → QR Code → TV Display</small>
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Technology Stack */}
      <section className="py-5" style={{background: 'var(--bg-secondary)'}}>
        <div className="container">
          <div className="text-center mb-5">
            <h2 className="display-4 fw-bold mb-3 text-primary">
              Built with Modern Technology
            </h2>
            <p className="lead text-secondary">
              Enterprise-grade technology stack for performance and reliability
            </p>
          </div>
          <div className="row g-4">
            <div className="col-lg-3 col-md-6 text-center">
              <div className="card hover-shadow h-100">
                <div className="card-body p-4">
                  <div className="feature-icon mb-3" style={{width: '60px', height: '60px', margin: '0 auto'}}>
                    ⚛️
                  </div>
                  <h5 className="fw-bold">React 19.1.0</h5>
                  <p className="text-secondary mb-0">Modern web dashboard with TypeScript</p>
                </div>
              </div>
            </div>
            <div className="col-lg-3 col-md-6 text-center">
              <div className="card hover-shadow h-100">
                <div className="card-body p-4">
                  <div className="feature-icon mb-3" style={{width: '60px', height: '60px', margin: '0 auto'}}>
                    📱
                  </div>
                  <h5 className="fw-bold">React Native</h5>
                  <p className="text-secondary mb-0">Cross-platform mobile apps</p>
                </div>
              </div>
            </div>
            <div className="col-lg-3 col-md-6 text-center">
              <div className="card hover-shadow h-100">
                <div className="card-body p-4">
                  <div className="feature-icon mb-3" style={{width: '60px', height: '60px', margin: '0 auto'}}>
                    🐍
                  </div>
                  <h5 className="fw-bold">Django REST</h5>
                  <p className="text-secondary mb-0">Robust backend API</p>
                </div>
              </div>
            </div>
            <div className="col-lg-3 col-md-6 text-center">
              <div className="card hover-shadow h-100">
                <div className="card-body p-4">
                  <div className="feature-icon mb-3" style={{width: '60px', height: '60px', margin: '0 auto'}}>
                    💳
                  </div>
                  <h5 className="fw-bold">Stripe</h5>
                  <p className="text-secondary mb-0">Secure payment processing</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-5" style={{background: 'var(--bg-primary)'}}>
        <div className="container">
          <div className="text-center mb-5">
            <h2 className="display-4 fw-bold mb-3 text-primary">
              Trusted by South African Businesses
            </h2>
            <p className="lead text-secondary">
              See what our customers say about the mobile-first approach
            </p>
          </div>
          <div className="row g-4">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="col-lg-4">
                <div className="card h-100 hover-shadow">
                  <div className="card-body p-4">
                    <div className="text-warning mb-3">
                      ⭐⭐⭐⭐⭐
                    </div>
                    <blockquote className="mb-4">
                      <p className="fst-italic">"{testimonial.quote}"</p>
                    </blockquote>
                    <div className="d-flex align-items-center">
                      <div className="rounded-circle bg-primary text-white d-flex align-items-center justify-content-center me-3" 
                           style={{width: '50px', height: '50px', fontSize: '1.5rem'}}>
                        {testimonial.author.charAt(0)}
                      </div>
                      <div>
                        <strong className="d-block">{testimonial.author}</strong>
                        <small className="text-secondary">
                          {testimonial.role}, {testimonial.company}
                        </small>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-5" style={{background: 'var(--primary-gradient)'}}>
        <div className="container text-center text-white">
          <div className="row justify-content-center">
            <div className="col-lg-8">
              <h2 className="display-4 fw-bold mb-3">
                Ready to Revolutionize Your Digital Signage?
              </h2>
              <p className="lead mb-4 opacity-90">
                Join the mobile-first revolution. Start your free trial today and experience 
                the future of digital signage management.
              </p>
              <div className="d-flex justify-content-center gap-3 flex-wrap">
                <Link to="/register" className="btn btn-light btn-lg px-5">
                  <strong>Start Free Trial</strong>
                </Link>
                <Link to="/pricing" className="btn btn-outline-light btn-lg px-5">
                  View Pricing
                </Link>
              </div>
              <p className="mt-4 opacity-75">
                <small>✨ No credit card required • 14-day free trial • Cancel anytime</small>
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
