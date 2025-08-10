import { useState } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Header from "../components/Header";
import MobileSidebar from "../components/MobileSidebar";

export default function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="d-flex">
      <MobileSidebar open={sidebarOpen} setOpen={setSidebarOpen} />
      <Sidebar />
      <div className="flex-grow-1 dashboard-content" style={{ backgroundColor: '#1a1b1e', color: '#e6e1e3' }}>
        <Header onMenuClick={() => setSidebarOpen(true)} />
        <main className="container-fluid py-4" style={{ backgroundColor: '#1a1b1e' }}>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
