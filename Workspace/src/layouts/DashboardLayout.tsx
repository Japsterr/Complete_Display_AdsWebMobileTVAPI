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
      <div className="flex-grow-1 dashboard-content">
        <Header onMenuClick={() => setSidebarOpen(true)} />
        <main className="container-fluid py-4">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
