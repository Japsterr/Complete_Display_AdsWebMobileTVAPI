import { XMarkIcon } from '@heroicons/react/24/outline';
import { NavLink, useLocation } from "react-router-dom";
import {
  HomeIcon,
  PhotoIcon,
  MegaphoneIcon,
  ComputerDesktopIcon,
  Cog6ToothIcon,
} from "@heroicons/react/24/outline";

const navigation = [
  { name: "Dashboard", href: "/dashboard", icon: HomeIcon },
  { name: "Media Library", href: "/media", icon: PhotoIcon },
  { name: "Campaigns", href: "/campaigns", icon: MegaphoneIcon },
  { name: "Displays", href: "/displays", icon: ComputerDesktopIcon },
  { name: "Settings", href: "/settings", icon: Cog6ToothIcon },
];

interface MobileSidebarProps {
  open: boolean;
  setOpen: (open: boolean) => void;
}

export default function MobileSidebar({ open, setOpen }: MobileSidebarProps) {
  const location = useLocation();

  if (!open) return null;

  return (
    <>
      <div className="mobile-sidebar-overlay d-md-none" onClick={() => setOpen(false)}></div>
      <nav className="mobile-sidebar d-md-none">
        <div className="d-flex flex-column h-100">
          <div className="flex-shrink-0 p-4 border-bottom border-secondary d-flex justify-content-between align-items-center">
            <div className="d-flex align-items-center">
              <div className="rounded p-2 bg-primary me-3">
                <span className="text-white fw-bold">D</span>
              </div>
              <h2 className="h5 mb-0 text-white fw-bold">DisplayAds</h2>
            </div>
            <button 
              className="btn btn-outline-light btn-sm"
              onClick={() => setOpen(false)}
            >
              <XMarkIcon style={{ width: "20px", height: "20px" }} />
            </button>
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
                        isActive ? "active" : "text-white-50"
                      }`}
                      onClick={() => setOpen(false)}
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
    </>
  );
}
