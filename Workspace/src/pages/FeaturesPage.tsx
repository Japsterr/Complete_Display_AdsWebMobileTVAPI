import { 
  ComputerDesktopIcon, 
  CalendarDaysIcon, 
  CloudIcon, 
  ChartBarIcon,
  CogIcon,
  ShieldCheckIcon 
} from "@heroicons/react/24/outline";

const features = [
  {
    icon: ComputerDesktopIcon,
    title: "Multi-Display Management",
    description: "Control hundreds of displays from a single dashboard. Monitor status, push updates, and manage content across your entire network.",
  },
  {
    icon: CalendarDaysIcon,
    title: "Advanced Scheduling",
    description: "Create complex scheduling rules with recurring events, date ranges, and time-based triggers. Perfect for promotions and announcements.",
  },
  {
    icon: CloudIcon,
    title: "Cloud-Based Platform",
    description: "Access your content and displays from anywhere. Our cloud infrastructure ensures 99.9% uptime and global content delivery.",
  },
  {
    icon: ChartBarIcon,
    title: "Analytics & Reporting",
    description: "Track display performance, content engagement, and system health with detailed analytics and automated reporting.",
  },
  {
    icon: CogIcon,
    title: "Easy Integration",
    description: "Connect with your existing systems via our REST API. Integrate with CRM, POS, and other business applications.",
  },
  {
    icon: ShieldCheckIcon,
    title: "Enterprise Security",
    description: "Bank-level security with encrypted connections, role-based access control, and compliance with industry standards.",
  },
];

export default function FeaturesPage() {
  return (
    <div className="py-5">
      <div className="container">
        <div className="text-center mb-5">
          <h1 className="display-4 fw-bold text-dark mb-4">
            Powerful Features for Digital Signage
          </h1>
          <p className="lead text-muted">
            Everything you need to create, manage, and deploy dynamic content across your display network.
          </p>
        </div>

        <div className="row g-4 mt-5">
          {features.map((feature, index) => (
            <div key={index} className="col-md-6 col-lg-4">
              <div className="card h-100 border-light shadow-sm">
                <div className="card-body p-4">
                  <feature.icon style={{ width: '48px', height: '48px' }} className="text-primary mb-3" />
                  <h3 className="h5 fw-semibold text-dark mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-muted mb-0">
                    {feature.description}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-5 p-4 p-lg-5 bg-light rounded">
          <div className="text-center">
            <h2 className="h3 fw-bold text-dark mb-4">
              Ready to transform your digital signage?
            </h2>
            <p className="lead text-muted mb-4">
              Join thousands of businesses already using DisplayAds to power their digital communications.
            </p>
            <div className="d-flex flex-column flex-sm-row gap-3 justify-content-center">
              <a
                href="/register"
                className="btn btn-primary btn-lg px-4"
              >
                Start Free Trial
              </a>
              <a
                href="/pricing"
                className="btn btn-outline-secondary btn-lg px-4"
              >
                View Pricing
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
