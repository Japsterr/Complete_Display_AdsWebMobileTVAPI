import { 
  BookOpenIcon, 
  PlayIcon, 
  CogIcon, 
  CommandLineIcon,
  QuestionMarkCircleIcon,
  DocumentTextIcon
} from "@heroicons/react/24/outline";

const documentationSections = [
  {
    icon: PlayIcon,
    title: "Getting Started",
    description: "Quick start guide to set up your first digital signage campaign",
    topics: [
      "Account Setup",
      "First Display Registration",
      "Upload Your First Media",
      "Create Your First Campaign",
      "Schedule Content",
    ]
  },
  {
    icon: CogIcon,
    title: "Display Management",
    description: "Learn how to manage and configure your displays",
    topics: [
      "Display Registration",
      "Remote Configuration",
      "Status Monitoring",
      "Troubleshooting Offline Displays",
      "Display Groups",
    ]
  },
  {
    icon: DocumentTextIcon,
    title: "Content Management",
    description: "Create and manage your digital signage content",
    topics: [
      "Supported File Formats",
      "Media Library Organization",
      "Content Scheduling",
      "Dynamic Content",
      "Template System",
    ]
  },
  {
    icon: CommandLineIcon,
    title: "API Documentation",
    description: "Integrate DisplayAds with your existing systems",
    topics: [
      "Authentication",
      "RESTful API Endpoints",
      "Webhooks",
      "Rate Limiting",
      "SDK Libraries",
    ]
  }
];

const quickLinks = [
  { title: "System Requirements", href: "#requirements" },
  { title: "Supported Formats", href: "#formats" },
  { title: "Billing & Pricing", href: "#billing" },
  { title: "Security & Privacy", href: "#security" },
  { title: "Service Status", href: "#status" },
  { title: "Release Notes", href: "#releases" },
];

export default function DocumentationPage() {
  return (
    <div className="py-5">
      <div className="container">
        <div className="text-center mb-5">
          <h1 className="display-4 fw-bold text-dark mb-4">
            Documentation
          </h1>
          <p className="lead text-muted">
            Everything you need to know about using DisplayAds for your digital signage needs.
          </p>
        </div>

        {/* Search Bar */}
        <div className="row justify-content-center mb-5">
          <div className="col-lg-6">
            <div className="input-group input-group-lg">
              <span className="input-group-text">
                <i className="bi bi-search"></i>
              </span>
              <input
                type="text"
                className="form-control"
                placeholder="Search documentation..."
              />
            </div>
          </div>
        </div>

        <div className="row g-5">
          {/* Main Documentation Sections */}
          <div className="col-lg-8">
            <div className="row g-4">
              {documentationSections.map((section, index) => (
                <div key={index} className="col-md-6">
                  <div className="card h-100 border-light shadow-sm">
                    <div className="card-body p-4">
                      <div className="d-flex align-items-center mb-3">
                        <section.icon style={{ width: '32px', height: '32px' }} className="text-primary me-3" />
                        <h3 className="h5 fw-semibold mb-0">{section.title}</h3>
                      </div>
                      <p className="text-muted mb-3">{section.description}</p>
                      <ul className="list-unstyled">
                        {section.topics.map((topic, topicIndex) => (
                          <li key={topicIndex} className="mb-2">
                            <a href="#" className="text-decoration-none d-flex align-items-center">
                              <i className="bi bi-arrow-right text-primary me-2"></i>
                              <span className="text-muted">{topic}</span>
                            </a>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Popular Guides */}
            <div className="mt-5">
              <h2 className="h3 fw-semibold mb-4">Popular Guides</h2>
              <div className="list-group">
                <a href="#" className="list-group-item list-group-item-action d-flex align-items-center">
                  <BookOpenIcon style={{ width: '20px', height: '20px' }} className="text-primary me-3" />
                  <div>
                    <h5 className="mb-1">Setting up your first display in 5 minutes</h5>
                    <p className="mb-1 text-muted">Step-by-step guide to get your display online and showing content.</p>
                    <small className="text-muted">Updated 2 days ago</small>
                  </div>
                </a>
                <a href="#" className="list-group-item list-group-item-action d-flex align-items-center">
                  <BookOpenIcon style={{ width: '20px', height: '20px' }} className="text-primary me-3" />
                  <div>
                    <h5 className="mb-1">Creating dynamic content with data feeds</h5>
                    <p className="mb-1 text-muted">Learn how to display real-time data from external sources.</p>
                    <small className="text-muted">Updated 1 week ago</small>
                  </div>
                </a>
                <a href="#" className="list-group-item list-group-item-action d-flex align-items-center">
                  <BookOpenIcon style={{ width: '20px', height: '20px' }} className="text-primary me-3" />
                  <div>
                    <h5 className="mb-1">Advanced scheduling techniques</h5>
                    <p className="mb-1 text-muted">Master complex scheduling scenarios and automation.</p>
                    <small className="text-muted">Updated 2 weeks ago</small>
                  </div>
                </a>
                <a href="#" className="list-group-item list-group-item-action d-flex align-items-center">
                  <BookOpenIcon style={{ width: '20px', height: '20px' }} className="text-primary me-3" />
                  <div>
                    <h5 className="mb-1">Troubleshooting common display issues</h5>
                    <p className="mb-1 text-muted">Solutions to the most common problems and how to fix them.</p>
                    <small className="text-muted">Updated 3 weeks ago</small>
                  </div>
                </a>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="col-lg-4">
            {/* Quick Links */}
            <div className="card border-light shadow-sm mb-4">
              <div className="card-body p-4">
                <h4 className="h5 fw-semibold mb-3">Quick Links</h4>
                <ul className="list-unstyled">
                  {quickLinks.map((link, index) => (
                    <li key={index} className="mb-2">
                      <a href={link.href} className="text-decoration-none d-flex align-items-center">
                        <i className="bi bi-link-45deg text-primary me-2"></i>
                        <span className="text-muted">{link.title}</span>
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Need Help */}
            <div className="card border-light shadow-sm mb-4">
              <div className="card-body p-4">
                <div className="d-flex align-items-center mb-3">
                  <QuestionMarkCircleIcon style={{ width: '24px', height: '24px' }} className="text-primary me-2" />
                  <h4 className="h5 fw-semibold mb-0">Need Help?</h4>
                </div>
                <p className="text-muted mb-3">
                  Can't find what you're looking for? Our support team is here to help.
                </p>
                <div className="d-grid gap-2">
                  <a href="/contact" className="btn btn-primary">
                    Contact Support
                  </a>
                  <a href="#" className="btn btn-outline-secondary">
                    Live Chat
                  </a>
                </div>
              </div>
            </div>

            {/* System Status */}
            <div className="card border-light shadow-sm">
              <div className="card-body p-4">
                <h4 className="h5 fw-semibold mb-3">System Status</h4>
                <div className="d-flex align-items-center mb-2">
                  <div className="bg-success rounded-circle me-2" style={{ width: '8px', height: '8px' }}></div>
                  <span className="small text-muted">All systems operational</span>
                </div>
                <div className="d-flex align-items-center mb-2">
                  <div className="bg-success rounded-circle me-2" style={{ width: '8px', height: '8px' }}></div>
                  <span className="small text-muted">API uptime: 99.9%</span>
                </div>
                <div className="d-flex align-items-center">
                  <div className="bg-success rounded-circle me-2" style={{ width: '8px', height: '8px' }}></div>
                  <span className="small text-muted">CDN performance: Good</span>
                </div>
                <a href="#" className="btn btn-sm btn-outline-primary mt-3">
                  View Status Page
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom CTA */}
        <div className="mt-5 p-4 p-lg-5 bg-light rounded text-center">
          <h2 className="h3 fw-semibold mb-3">Still have questions?</h2>
          <p className="text-muted mb-4">
            Our documentation is constantly updated. If you can't find what you need, reach out to our team.
          </p>
          <div className="d-flex flex-column flex-sm-row gap-3 justify-content-center">
            <a href="/contact" className="btn btn-primary">
              Contact Support
            </a>
            <a href="#" className="btn btn-outline-secondary">
              Request Feature
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
