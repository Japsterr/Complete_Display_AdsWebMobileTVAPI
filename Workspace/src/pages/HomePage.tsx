import { Link } from "react-router-dom";

const features = [
  {
    icon: "bi-display",
    title: "Digital Signage Management",
    desc: "Easily manage content across all your digital displays from one central dashboard.",
  },
  {
    icon: "bi-calendar-event",
    title: "Campaign Scheduling", 
    desc: "Schedule campaigns to run at exactly the right time across your display network.",
  },
  {
    icon: "bi-gear",
    title: "Remote Display Control",
    desc: "Monitor and control all your displays remotely with real-time status updates.",
  },
];

const testimonials = [
  {
    quote: "DisplayAds transformed how we manage our retail promotions across 50+ locations.",
    author: "Sarah Johnson",
    company: "RetailCorp",
  },
  {
    quote: "The scheduling features saved us hours of manual work every week.",
    author: "Mike Chen", 
    company: "TechStart Inc",
  },
];

export default function HomePage() {
  return (
    <div>
      {/* Hero Section */}
      <section className="bg-light py-5">
        <div className="container">
          <div className="row justify-content-center text-center">
            <div className="col-lg-8">
              <h1 className="display-4 fw-bold mb-4">
                Transform Your Business with{' '}
                <span className="text-primary">Digital Signage</span>
              </h1>
              <p className="lead mb-4">
                Manage, schedule, and display dynamic content across your entire network of digital signs with our powerful SaaS platform.
              </p>
              <div className="d-flex gap-3 justify-content-center">
                <Link to="/register" className="btn btn-primary btn-lg">
                  Start Free Trial
                </Link>
                <Link to="/features" className="btn btn-outline-secondary btn-lg">
                  Learn More
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Overview */}
      <section className="py-5">
        <div className="container">
          <div className="text-center mb-5">
            <h2 className="display-5 fw-bold mb-3">
              Everything you need to manage digital signage
            </h2>
            <p className="lead text-muted">
              Our platform provides all the tools you need to create, manage, and deploy content across your display network.
            </p>
          </div>
          <div className="row g-4 mt-5">
            {features.map((feature, index) => (
              <div key={index} className="col-md-4">
                <div className="card h-100 shadow-sm border-0">
                  <div className="card-body text-center p-4">
                    <i className={`${feature.icon} text-primary mb-3`} style={{fontSize: '3rem'}}></i>
                    <h3 className="card-title h5 mb-3">{feature.title}</h3>
                    <p className="card-text text-muted">{feature.desc}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Social Proof */}
      <section className="bg-light py-5">
        <div className="container">
          <div className="text-center mb-5">
            <h2 className="display-5 fw-bold mb-4">
              Trusted by businesses worldwide
            </h2>
          </div>
          <div className="row g-4">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="col-md-6">
                <div className="card h-100 border-0 shadow-sm">
                  <div className="card-body">
                    <blockquote className="blockquote">
                      <p className="mb-3 fst-italic">"{testimonial.quote}"</p>
                    </blockquote>
                    <footer className="blockquote-footer">
                      <strong>{testimonial.author}</strong>
                      <cite title="Source Title"> - {testimonial.company}</cite>
                    </footer>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="bg-primary py-5 text-white">
        <div className="container text-center">
          <h2 className="display-5 fw-bold mb-3">
            Ready to get started?
          </h2>
          <p className="lead mb-4">
            Join thousands of businesses using DisplayAds to power their digital signage.
          </p>
          <Link to="/register" className="btn btn-light btn-lg">
            Start Your Free Trial
          </Link>
        </div>
      </section>
    </div>
  );
}
