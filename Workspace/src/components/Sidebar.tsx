import { NavLink, useLocation } from "react-router-dom";
import {
  HomeIcon,
  PhotoIcon,
  MegaphoneIcon,
  ComputerDesktopIcon,
  Cog6ToothIcon,
  UserIcon,
  ChartBarIcon,
  RectangleGroupIcon,
} from "@heroicons/react/24/outline";

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: HomeIcon },
  { name: "Profile", href: "/profile", icon: UserIcon },
  { name: "Campaigns", href: "/campaigns", icon: MegaphoneIcon },
  { name: "Media", href: "/media", icon: PhotoIcon },
  { name: "Menus", href: "/menus", icon: RectangleGroupIcon },
  { name: "Displays", href: "/displays", icon: ComputerDesktopIcon },
  { name: "Analytics", href: "/analytics", icon: ChartBarIcon },
  { name: "Settings", href: "/settings", icon: Cog6ToothIcon },
];

export default function Sidebar() {
  const location = useLocation();

  return (
    <nav className="sidebar d-flex" style={{ backgroundColor: '#1a1b1e', borderRight: '1px solid rgba(255,107,53,0.25)' }}>
      <div className="d-flex flex-column h-100">
        <div className="flex-shrink-0 p-4" style={{ borderBottom: '1px solid rgba(255,107,53,0.25)' }}>
          <div className="d-flex align-items-center">
            <div className="rounded p-2 me-3" style={{ background: 'linear-gradient(135deg, #ff6b35 0%, #ff925f 100%)' }}>
              <span className="fw-bold" style={{ color: '#1a1b1e' }}>D</span>
            </div>
            <h2 className="h5 mb-0 text-white fw-bold">DisplayAds</h2>
          </div>
        </div>
        <div className="flex-grow-1 p-3">
          <ul className="nav nav-pills flex-column">
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.href;
              return (
                <li key={item.name} className="nav-item mb-2">
                  <NavLink
                    to={item.href}
                    className={`nav-link d-flex align-items-center px-3 py-2 ${
                      isActive ? "active" : ""
                    }`}
                    style={{ color: isActive ? '#1a1b1e' : '#cbd5e0', backgroundColor: isActive ? '#ff6b35' : 'transparent' }}
                  >
                    <Icon className="me-3" style={{ width: "20px", height: "20px" }} />
                    {item.name}
                  </NavLink>
                </li>
              );
            })}
          </ul>
        </div>
      </div>
    </nav>
  );
}
