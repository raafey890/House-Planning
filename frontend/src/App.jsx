import { BrowserRouter, Routes, Route } from "react-router-dom";

import HomePage from "./pages/Home/HomePage.jsx";

import PlannerPage from "./pages/Planner/PlannerPage.jsx";

import GalleryPage from "./pages/Gallery/GalleryPage.jsx";

import FloorPlanPage from "./pages/FloorPlan/FloorPlanPage.jsx";

import EstimatorPage from "./pages/Estimator/EstimatorPage.jsx";

import AIStudioPage from "./pages/AIStudio/AIStudioPage.jsx";

import DashboardPage from "./pages/Dashboard/DashboardPage.jsx";

import MarketplacePage from "./pages/marketplaceui/MarketplacePage.jsx";

import LoginPage from "./pages/Auth/LoginPage.jsx";

import SignupPage from "./pages/Auth/SignupPage.jsx";

import PremiumPage from "./pages/Premium/PremiumPage.jsx";

import SettingsPage from "./pages/Settings/SettingsPage.jsx";

import ProfilePage from "./pages/Profile/ProfilePage.jsx";

import SupportPage from "./pages/Support/SupportPage.jsx";

import NotFoundPage from "./pages/NotFound/NotFoundPage.jsx";

function App() {

    return (

        <BrowserRouter>

            <Routes>

                <Route path="/" element={<HomePage />} />

                <Route path="/planner" element={<PlannerPage />} />

                <Route path="/gallery" element={<GalleryPage />} />

                <Route path="/floorplan" element={<FloorPlanPage />} />

                <Route path="/estimator" element={<EstimatorPage />} />

                <Route path="/ai-studio" element={<AIStudioPage />} />

                <Route path="/dashboard" element={<DashboardPage />} />

                <Route path="/marketplace" element={<MarketplacePage />} />

                <Route path="/login" element={<LoginPage />} />

                <Route path="/signup" element={<SignupPage />} />

                <Route path="/premium" element={<PremiumPage />} />

                <Route path="/settings" element={<SettingsPage />} />

                <Route path="/profile" element={<ProfilePage />} />

                <Route path="/support" element={<SupportPage />} />

                <Route path="*" element={<NotFoundPage />} />

            </Routes>

        </BrowserRouter>

    );

}

export default App;