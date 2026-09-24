import { useEffect } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { useAuthStore } from "./store";

import HomePage from "./pages/Home/HomePage.jsx";
import PlannerPage from "./pages/planner/PlannerPage.jsx";
import GalleryPage from "./pages/Gallery/GalleryPage.jsx";
import FloorPlanPage from "./pages/FloorPlan/FloorPlanPage.jsx";
import EstimatorPage from "./pages/Estimator/EstimatorPage.jsx";
import AIStudioPage from "./pages/AIStudio/AIStudioPage.jsx";
import DashboardPage from "./pages/Dashboard/DashboardPage.jsx";
import MarketplacePage from "./pages/MarketPlaceUi/MarketplacePage.jsx";
import LoginPage from "./pages/Auth/LoginPage.jsx";
import SignupPage from "./pages/Auth/SignupPage.jsx";
import PremiumPage from "./pages/Premium/PremiumPage.jsx";
import SettingsPage from "./pages/Settings/SettingsPage.jsx";
import ProfilePage from "./pages/Profile/ProfilePage.jsx";
import SupportPage from "./pages/Support/SupportPage.jsx";
import NotFoundPage from "./pages/NotFound/NotFoundPage.jsx";

// F3 Additions
import ProtectedRoute from "./routes/ProtectedRoute.jsx";
import AppLayout from "./layouts/AppLayout.jsx";
import ProjectsPage from "./pages/Projects/ProjectsPage.jsx";
import ProjectWorkspace from "./pages/Projects/ProjectWorkspace.jsx";

function App() {
  const initializeAuth = useAuthStore((state) => state.initializeAuth);

  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/gallery" element={<GalleryPage />} />
        <Route path="/marketplace" element={<MarketplacePage />} />
        <Route path="/premium" element={<PremiumPage />} />
        <Route path="/support" element={<SupportPage />} />

        {/* Authenticated Application Layout */}
        <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/projects" element={<ProjectsPage />} />
          <Route path="/projects/:id" element={<ProjectWorkspace />} />
          <Route path="/projects/:id/planner" element={<PlannerPage />} />
          
          {/* Legacy / un-nested routes for now */}
          <Route path="/planner" element={<PlannerPage />} />
          <Route path="/floorplan" element={<FloorPlanPage />} />
          <Route path="/estimator" element={<EstimatorPage />} />
          <Route path="/ai-studio" element={<AIStudioPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="/profile" element={<ProfilePage />} />
        </Route>

        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;