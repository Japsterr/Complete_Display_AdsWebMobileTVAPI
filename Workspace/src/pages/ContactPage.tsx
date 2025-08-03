import { EnvelopeIcon, PhoneIcon, MapPinIcon } from "@heroicons/react/24/outline";

export default function ContactPage() {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle form submission
    alert("Thank you for your message! We'll get back to you soon.");
  };

  return (
    <div className="py-5">
      <div className="container">
        <div className="text-center mb-5">
          <h1 className="display-4 fw-bold text-dark mb-4">
            Contact Us
          </h1>
          <p className="lead text-muted">
            Get in touch with our team. We're here to help you succeed with your digital signage needs.
          </p>
        </div>

        <div className="row g-5">
          {/* Contact Form */}
          <div className="col-lg-8">
            <div className="card border-light shadow-sm">
              <div className="card-body p-4">
                <h3 className="h4 fw-semibold mb-4">Send us a message</h3>
                <form onSubmit={handleSubmit}>
                  <div className="row g-3">
                    <div className="col-md-6">
                      <label htmlFor="firstName" className="form-label">
                        First Name *
                      </label>
                      <input
                        type="text"
                        className="form-control"
                        id="firstName"
                        required
                      />
                    </div>
                    <div className="col-md-6">
                      <label htmlFor="lastName" className="form-label">
                        Last Name *
                      </label>
                      <input
                        type="text"
                        className="form-control"
                        id="lastName"
                        required
                      />
                    </div>
                    <div className="col-12">
                      <label htmlFor="email" className="form-label">
                        Email Address *
                      </label>
                      <input
                        type="email"
                        className="form-control"
                        id="email"
                        required
                      />
                    </div>
                    <div className="col-12">
                      <label htmlFor="company" className="form-label">
                        Company
                      </label>
                      <input
                        type="text"
                        className="form-control"
                        id="company"
                      />
                    </div>
                    <div className="col-12">
                      <label htmlFor="subject" className="form-label">
                        Subject *
                      </label>
                      <select className="form-select" id="subject" required>
                        <option value="">Select a topic</option>
                        <option value="sales">Sales Inquiry</option>
                        <option value="support">Technical Support</option>
                        <option value="billing">Billing Question</option>
                        <option value="partnership">Partnership</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                    <div className="col-12">
                      <label htmlFor="message" className="form-label">
                        Message *
                      </label>
                      <textarea
                        className="form-control"
                        id="message"
                        rows={6}
                        placeholder="Tell us how we can help you..."
                        required
                      ></textarea>
                    </div>
                    <div className="col-12">
                      <button type="submit" className="btn btn-primary btn-lg">
                        Send Message
                      </button>
                    </div>
                  </div>
                </form>
              </div>
            </div>
          </div>

          {/* Contact Information */}
          <div className="col-lg-4">
            <div className="card border-light shadow-sm h-100">
              <div className="card-body p-4">
                <h3 className="h4 fw-semibold mb-4">Get in touch</h3>
                
                <div className="d-flex align-items-start mb-4">
                  <EnvelopeIcon style={{ width: '24px', height: '24px' }} className="text-primary flex-shrink-0 mt-1" />
                  <div className="ms-3">
                    <h5 className="h6 fw-semibold mb-1">Email</h5>
                    <p className="text-muted mb-0">
                      <a href="mailto:support@displayads.com" className="text-decoration-none">
                        support@displayads.com
                      </a>
                    </p>
                    <p className="text-muted mb-0">
                      <a href="mailto:sales@displayads.com" className="text-decoration-none">
                        sales@displayads.com
                      </a>
                    </p>
                  </div>
                </div>

                <div className="d-flex align-items-start mb-4">
                  <PhoneIcon style={{ width: '24px', height: '24px' }} className="text-primary flex-shrink-0 mt-1" />
                  <div className="ms-3">
                    <h5 className="h6 fw-semibold mb-1">Phone</h5>
                    <p className="text-muted mb-0">+1 (555) 123-4567</p>
                    <p className="text-muted mb-0 small">Mon-Fri 9AM-6PM EST</p>
                  </div>
                </div>

                <div className="d-flex align-items-start mb-4">
                  <MapPinIcon style={{ width: '24px', height: '24px' }} className="text-primary flex-shrink-0 mt-1" />
                  <div className="ms-3">
                    <h5 className="h6 fw-semibold mb-1">Office</h5>
                    <p className="text-muted mb-0">
                      123 Digital Street<br />
                      Tech City, TC 12345<br />
                      United States
                    </p>
                  </div>
                </div>

                <hr className="my-4" />

                <div>
                  <h5 className="h6 fw-semibold mb-3">Response Times</h5>
                  <div className="small text-muted">
                    <p className="mb-2">
                      <strong>Sales:</strong> Within 1 hour
                    </p>
                    <p className="mb-2">
                      <strong>Support:</strong> Within 4 hours
                    </p>
                    <p className="mb-0">
                      <strong>General:</strong> Within 24 hours
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* FAQ Section */}
        <div className="mt-5">
          <div className="text-center mb-4">
            <h2 className="h3 fw-semibold">Frequently Asked Questions</h2>
          </div>
          <div className="row g-4">
            <div className="col-md-6">
              <div className="card border-0 bg-light">
                <div className="card-body p-4">
                  <h5 className="fw-semibold mb-3">Do you offer free trials?</h5>
                  <p className="text-muted mb-0">
                    Yes! All plans include a 14-day free trial with full access to features.
                  </p>
                </div>
              </div>
            </div>
            <div className="col-md-6">
              <div className="card border-0 bg-light">
                <div className="card-body p-4">
                  <h5 className="fw-semibold mb-3">What payment methods do you accept?</h5>
                  <p className="text-muted mb-0">
                    We accept all major credit cards, PayPal, and wire transfers for enterprise accounts.
                  </p>
                </div>
              </div>
            </div>
            <div className="col-md-6">
              <div className="card border-0 bg-light">
                <div className="card-body p-4">
                  <h5 className="fw-semibold mb-3">Can I cancel anytime?</h5>
                  <p className="text-muted mb-0">
                    Absolutely. You can cancel your subscription at any time with no cancellation fees.
                  </p>
                </div>
              </div>
            </div>
            <div className="col-md-6">
              <div className="card border-0 bg-light">
                <div className="card-body p-4">
                  <h5 className="fw-semibold mb-3">Do you provide setup assistance?</h5>
                  <p className="text-muted mb-0">
                    Yes, our team provides free setup assistance and onboarding for all new customers.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
