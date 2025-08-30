import { BrowserRouter, Routes, Route } from "react-router-dom";
import PublicLayout from "./layouts/PublicLayout";
import HomePage from "./pages/HomePage";
import FeaturesPage from "./pages/FeaturesPage";
import PricingPage from "./pages/PricingPage";
import ContactPage from "./pages/ContactPage";
import DocumentationPage from "./pages/DocumentationPage";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardLayout from "./layouts/DashboardLayout";
import ProtectedRoute from "./components/ProtectedRoute";
import DashboardPage from "./pages/DashboardPage";
import ProfilePage from "./pages/ProfilePage";
import DisplayManagementPage from "./pages/DisplayManagementPage";
import DisplayDetailPage from "./pages/DisplayDetailPage";
import RegisterDisplayPage from "./pages/RegisterDisplayPage";
import SettingsPage from "./pages/SettingsPage";
import MediaLibraryPage from "./pages/MediaLibraryPage";
import CampaignsPage from "./pages/CampaignsPage";
import CampaignEditor from "./pages/CampaignEditor";
import CampaignMediaEditor from "./pages/CampaignMediaEditor";
import ApiTestPage from "./pages/ApiTestPage";
import AnalyticsPage from "./pages/AnalyticsPage";
import MenuManagementPage from "./pages/MenuManagementPage";
import MenuEditor from "./pages/MenuEditor";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<PublicLayout />}>
          <Route path="/" element={<HomePage />} />
          <Route path="/features" element={<FeaturesPage />} />
          <Route path="/pricing" element={<PricingPage />} />
          <Route path="/contact" element={<ContactPage />} />
          <Route path="/documentation" element={<DocumentationPage />} />
        </Route>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/api-test" element={<ApiTestPage />} />
          <Route path="/media" element={<MediaLibraryPage />} />
          <Route path="/campaigns" element={<CampaignsPage />} />
          <Route path="/campaigns/new" element={<CampaignEditor />} />
          <Route path="/campaigns/:id/edit" element={<CampaignEditor />} />
          <Route path="/campaigns/:campaignId/media" element={<CampaignMediaEditor />} />
          <Route path="/displays" element={<DisplayManagementPage />} />
          <Route path="/displays/new" element={<RegisterDisplayPage />} />
          <Route path="/displays/:id" element={<DisplayDetailPage />} />
          <Route path="/menus" element={<MenuManagementPage />} />
          <Route path="/menus/new" element={<MenuEditor />} />
          <Route path="/menus/:id/edit" element={<MenuEditor />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
