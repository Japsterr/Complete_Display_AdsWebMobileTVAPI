import { Outlet } from "react-router-dom";
import PublicNavbar from "../components/PublicNavbar";
import Footer from "../components/Footer";

export default function PublicLayout() {
  return (
    <div className="d-flex flex-column min-vh-100 public-dark">
      <PublicNavbar />
      <main className="flex-grow-1" style={{ backgroundColor: '#1d1f23' }}>
        <Outlet />
      </main>
      <Footer />
    </div>
  );
}
