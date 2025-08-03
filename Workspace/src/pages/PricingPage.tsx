import React from 'react';
import { Link } from 'react-router-dom';

const PricingPage: React.FC = () => {
  const plans = [
    {
      name: 'Free',
      price: 'R0',
      period: '/month',
      description: 'Perfect for getting started with digital signage',
      popular: false,
      features: [
        '3 Campaigns',
        '5 Displays',
        '10 Images only',
        '1 User account',
        'Basic analytics',
        'Community support',
        'QR code activation'
      ],
      limitations: [
        'No video support',
        'Limited storage (500MB)',
        'Basic scheduling only'
      ],
      buttonText: 'Start Free',
      buttonClass: 'btn-outline-primary'
    },
    {
      name: 'Starter',
      price: 'R99',
      period: '/month',
      description: 'Ideal for small businesses and growing operations',
      popular: true,
      features: [
        '15 Campaigns',
        '25 Displays',
        '100 Images + 20 Videos',
        '3 User accounts',
        '10GB Storage',
        'Full analytics & reporting',
        'Email support',
        'Priority scheduling',
        'QR code activation'
      ],
      limitations: [],
      buttonText: 'Choose Starter',
      buttonClass: 'btn-primary'
    },
    {
      name: 'Professional',
      price: 'R499',
      period: '/month',
      description: 'Complete solution for professional digital signage networks',
      popular: false,
      features: [
        'Unlimited Campaigns',
        '100 Displays',
        'Unlimited Images + Videos',
        '10 User accounts',
        'Unlimited Storage',
        'Advanced analytics + API',
        'Priority support + phone',
        'Custom branding',
        'Advanced scheduling',
        'QR code activation'
      ],
      limitations: [],
      buttonText: 'Choose Professional',
      buttonClass: 'btn-primary'
    }
  ];

  const faqs = [
    {
      question: 'What is QR code activation?',
      answer: 'Our revolutionary feature lets you activate any TV display by simply scanning a QR code with your mobile app. No manual setup required!'
    },
    {
      question: 'Can I upgrade or downgrade my plan?',
      answer: 'Yes, you can change your plan anytime. Upgrades take effect immediately, downgrades at the next billing cycle.'
    },
    {
      question: 'What happens if I exceed my limits?',
      answer: 'We\'ll notify you when approaching limits. You can upgrade your plan or archive old content to stay within limits.'
    },
    {
      question: 'Do you offer discounts for annual billing?',
      answer: 'Yes! Save 20% by choosing annual billing on any paid plan. Contact us for enterprise pricing.'
    },
    {
      question: 'Is there a setup fee?',
      answer: 'No setup fees ever! All plans include full access to our web dashboard, mobile apps, and TV software.'
    }
  ];

  return (
    <div className="pricing-page">
      {/* Hero Section */}
      <section className="hero-section text-center">
        <div className="container">
          <div className="row justify-content-center">
            <div className="col-lg-8">
              <div className="mobile-first-badge fade-in">
                💰 Transparent Pricing • No Hidden Fees
              </div>
              <h1 className="hero-title fade-in">
                Choose Your{' '}
                <span style={{background: 'var(--secondary-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent'}}>
                  Perfect Plan
                </span>
              </h1>
              <p className="hero-subtitle fade-in">
                Start free and scale as you grow. All plans include QR code activation, 
                mobile apps, and our complete digital signage ecosystem.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="py-5" style={{background: 'var(--bg-primary)'}}>
        <div className="container">
          <div className="row g-4 justify-content-center">
            {plans.map((plan, index) => (
              <div key={index} className="col-lg-4 col-md-6">
                <div className={`pricing-card ${plan.popular ? 'featured' : ''} hover-scale`}>
                  {plan.popular && (
                    <div className="popular-badge">
                      ⭐ Most Popular
                    </div>
                  )}
                  <div className="text-center mb-4">
                    <h3 className="fw-bold text-primary mb-2">{plan.name}</h3>
                    <div className="price-display">
                      <span className="price">{plan.price}</span>
                      <span className="period text-secondary">{plan.period}</span>
                    </div>
                    <p className="text-secondary">{plan.description}</p>
                  </div>

                  <div className="features-list mb-4">
                    <h6 className="fw-bold text-success mb-3">✅ What's Included:</h6>
                    <ul className="list-unstyled">
                      {plan.features.map((feature, idx) => (
                        <li key={idx} className="mb-2">
                          <span className="text-success me-2">✓</span>
                          {feature}
                        </li>
                      ))}
                    </ul>

                    {plan.limitations.length > 0 && (
                      <>
                        <h6 className="fw-bold text-warning mb-3 mt-4">⚠️ Limitations:</h6>
                        <ul className="list-unstyled">
                          {plan.limitations.map((limitation, idx) => (
                            <li key={idx} className="mb-2 text-secondary">
                              <span className="text-warning me-2">−</span>
                              {limitation}
                            </li>
                          ))}
                        </ul>
                      </>
                    )}
                  </div>

                  <div className="text-center">
                    <Link 
                      to={plan.name === 'Free' ? '/register' : '/register?plan=' + plan.name.toLowerCase()} 
                      className={`btn ${plan.buttonClass} btn-lg w-100`}
                    >
                      {plan.buttonText}
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Value Proposition */}
          <div className="row mt-5">
            <div className="col-12">
              <div className="card text-center" style={{background: 'var(--primary-gradient)', color: 'white', border: 'none'}}>
                <div className="card-body p-5">
                  <h3 className="fw-bold mb-4">🇿🇦 Built for South African Businesses</h3>
                  <div className="row">
                    <div className="col-md-3 mb-3">
                      <div className="h4">💳</div>
                      <strong>ZAR Currency</strong><br/>
                      <small>Local pricing & billing</small>
                    </div>
                    <div className="col-md-3 mb-3">
                      <div className="h4">📱</div>
                      <strong>Mobile-First</strong><br/>
                      <small>QR code activation</small>
                    </div>
                    <div className="col-md-3 mb-3">
                      <div className="h4">🔒</div>
                      <strong>Secure</strong><br/>
                      <small>Enterprise-grade security</small>
                    </div>
                    <div className="col-md-3 mb-3">
                      <div className="h4">⚡</div>
                      <strong>Fast Setup</strong><br/>
                      <small>Live in minutes</small>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Comparison Table */}
      <section className="py-5" style={{background: 'var(--bg-secondary)'}}>
        <div className="container">
          <div className="text-center mb-5">
            <h2 className="display-4 fw-bold text-primary mb-3">
              Feature Comparison
            </h2>
            <p className="lead text-secondary">
              See exactly what's included in each plan
            </p>
          </div>

          <div className="table-responsive">
            <table className="table table-striped">
              <thead>
                <tr>
                  <th>Feature</th>
                  <th className="text-center">Free</th>
                  <th className="text-center">Starter</th>
                  <th className="text-center">Professional</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><strong>Campaigns</strong></td>
                  <td className="text-center">3</td>
                  <td className="text-center">15</td>
                  <td className="text-center">Unlimited</td>
                </tr>
                <tr>
                  <td><strong>Displays</strong></td>
                  <td className="text-center">5</td>
                  <td className="text-center">25</td>
                  <td className="text-center">100</td>
                </tr>
                <tr>
                  <td><strong>Images</strong></td>
                  <td className="text-center">10</td>
                  <td className="text-center">100</td>
                  <td className="text-center">Unlimited</td>
                </tr>
                <tr>
                  <td><strong>Videos</strong></td>
                  <td className="text-center"><span className="text-danger">❌</span></td>
                  <td className="text-center">20</td>
                  <td className="text-center">Unlimited</td>
                </tr>
                <tr>
                  <td><strong>User Accounts</strong></td>
                  <td className="text-center">1</td>
                  <td className="text-center">3</td>
                  <td className="text-center">10</td>
                </tr>
                <tr>
                  <td><strong>Storage</strong></td>
                  <td className="text-center">500MB</td>
                  <td className="text-center">10GB</td>
                  <td className="text-center">Unlimited</td>
                </tr>
                <tr>
                  <td><strong>QR Code Activation</strong></td>
                  <td className="text-center"><span className="text-success">✅</span></td>
                  <td className="text-center"><span className="text-success">✅</span></td>
                  <td className="text-center"><span className="text-success">✅</span></td>
                </tr>
                <tr>
                  <td><strong>Mobile Apps</strong></td>
                  <td className="text-center"><span className="text-success">✅</span></td>
                  <td className="text-center"><span className="text-success">✅</span></td>
                  <td className="text-center"><span className="text-success">✅</span></td>
                </tr>
                <tr>
                  <td><strong>Advanced Analytics</strong></td>
                  <td className="text-center"><span className="text-danger">❌</span></td>
                  <td className="text-center"><span className="text-success">✅</span></td>
                  <td className="text-center"><span className="text-success">✅</span></td>
                </tr>
                <tr>
                  <td><strong>API Access</strong></td>
                  <td className="text-center"><span className="text-danger">❌</span></td>
                  <td className="text-center"><span className="text-danger">❌</span></td>
                  <td className="text-center"><span className="text-success">✅</span></td>
                </tr>
                <tr>
                  <td><strong>Custom Branding</strong></td>
                  <td className="text-center"><span className="text-danger">❌</span></td>
                  <td className="text-center"><span className="text-danger">❌</span></td>
                  <td className="text-center"><span className="text-success">✅</span></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-5" style={{background: 'var(--bg-primary)'}}>
        <div className="container">
          <div className="text-center mb-5">
            <h2 className="display-4 fw-bold text-primary mb-3">
              Frequently Asked Questions
            </h2>
          </div>

          <div className="row justify-content-center">
            <div className="col-lg-8">
              <div className="accordion" id="pricingFAQ">
                {faqs.map((faq, index) => (
                  <div key={index} className="accordion-item">
                    <h2 className="accordion-header">
                      <button 
                        className="accordion-button collapsed" 
                        type="button" 
                        data-bs-toggle="collapse" 
                        data-bs-target={`#faq${index}`}
                      >
                        {faq.question}
                      </button>
                    </h2>
                    <div 
                      id={`faq${index}`} 
                      className="accordion-collapse collapse" 
                      data-bs-parent="#pricingFAQ"
                    >
                      <div className="accordion-body">
                        {faq.answer}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Call to Action */}
      <section className="py-5" style={{background: 'var(--secondary-gradient)'}}>
        <div className="container text-center text-white">
          <div className="row justify-content-center">
            <div className="col-lg-8">
              <h2 className="display-4 fw-bold mb-3">
                Ready to Get Started?
              </h2>
              <p className="lead mb-4 opacity-90">
                Start with our free plan and upgrade as you grow. 
                No contracts, no setup fees, cancel anytime.
              </p>
              <div className="d-flex justify-content-center gap-3 flex-wrap">
                <Link to="/register" className="btn btn-light btn-lg px-5">
                  <strong>Start Free Trial</strong>
                </Link>
                <Link to="/contact" className="btn btn-outline-light btn-lg px-5">
                  Contact Sales
                </Link>
              </div>
              <p className="mt-4 opacity-75">
                <small>✨ All plans include 14-day free trial • Cancel anytime • No credit card required for Free plan</small>
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default PricingPage;
