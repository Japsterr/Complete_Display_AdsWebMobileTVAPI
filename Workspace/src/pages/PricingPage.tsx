import { CheckIcon } from "@heroicons/react/20/solid";
import { Link } from "react-router-dom";

const plans = [
  {
    name: "Starter",
    price: "$29",
    description: "Perfect for small businesses with a few displays",
    features: [
      "Up to 5 displays",
      "Basic scheduling",
      "Media library",
      "Email support",
      "Mobile app access",
    ],
    popular: false,
  },
  {
    name: "Professional",
    price: "$99",
    description: "Great for growing businesses with multiple locations",
    features: [
      "Up to 25 displays",
      "Advanced scheduling",
      "Team collaboration",
      "Priority support",
      "Analytics dashboard",
      "API access",
    ],
    popular: true,
  },
  {
    name: "Enterprise",
    price: "$299",
    description: "For large organizations with extensive display networks",
    features: [
      "Unlimited displays",
      "Custom integrations",
      "Dedicated support",
      "SLA guarantee",
      "White-label options",
      "Advanced analytics",
    ],
    popular: false,
  },
];

export default function PricingPage() {
  return (
    <div className="py-5">
      <div className="container">
        <div className="text-center mb-5">
          <h1 className="display-4 fw-bold text-dark mb-4">
            Simple, transparent pricing
          </h1>
          <p className="lead text-muted">
            Choose the plan that fits your business needs. All plans include a 14-day free trial.
          </p>
        </div>

        <div className="row g-4 mt-5">
          {plans.map((plan) => (
            <div key={plan.name} className="col-lg-4">
              <div
                className={`card h-100 position-relative ${
                  plan.popular
                    ? "border-primary shadow"
                    : "border-light shadow-sm"
                }`}
              >
                {plan.popular && (
                  <div className="position-absolute top-0 start-50 translate-middle">
                    <span className="badge bg-primary px-3 py-1">
                      Most Popular
                    </span>
                  </div>
                )}
                
                <div className="card-body p-4 text-center">
                  <h3 className="h4 fw-semibold text-dark">{plan.name}</h3>
                  <p className="text-muted mt-2">{plan.description}</p>
                  <div className="mt-4">
                    <span className="display-5 fw-bold text-dark">{plan.price}</span>
                    <span className="text-muted">/month</span>
                  </div>
                </div>

                <div className="card-body pt-0">
                  <ul className="list-unstyled">
                    {plan.features.map((feature) => (
                      <li key={feature} className="d-flex align-items-start mb-3">
                        <CheckIcon style={{ width: '20px', height: '20px' }} className="text-primary flex-shrink-0 mt-1" />
                        <span className="ms-3 text-muted">{feature}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="card-footer bg-transparent border-0 p-4">
                  <Link
                    to="/register"
                    className={`btn w-100 ${
                      plan.popular
                        ? "btn-primary"
                        : "btn-outline-secondary"
                    }`}
                  >
                    Start free trial
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-5 text-center">
          <p className="text-muted mb-3">
            Need a custom plan? Have questions about our pricing?
          </p>
          <Link
            to="/contact"
            className="text-primary text-decoration-none fw-medium"
          >
            Contact our sales team
          </Link>
        </div>
      </div>
    </div>
  );
}
