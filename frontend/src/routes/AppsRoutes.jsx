import { BrowserRouter, Routes, Route } from "react-router-dom";

import HomePage from "../pages/Home/HomePage";
import PlannerPage from "../pages/Planner/PlannerPage";
import GalleryPage from "../pages/Gallery/GalleryPage";
import PremiumPage from "../pages/Premium/PremiumPage";
import DashboardPage from "../pages/Dashboard/DashboardPage";
import LoginPage from "../pages/Auth/LoginPage";
import SignupPage from "../pages/Auth/SignupPage";

import ProtectedRoute from "./ProtectedRoute";

function AppRoutes() {

    return (

        <BrowserRouter>

            <Routes>

                <Route
                    path="/"
                    element={<HomePage />}
                />

                <Route
                    path="/planner"
                    element={<PlannerPage />}
                />

                <Route
                    path="/gallery"
                    element={<GalleryPage />}
                />

                <Route
                    path="/premium"
                    element={<PremiumPage />}
                />

                <Route
                    path="/login"
                    element={<LoginPage />}
                />

                <Route
                    path="/signup"
                    element={<SignupPage />}
                />

                <Route
                    path="/dashboard"
                    element={
                        <ProtectedRoute>

                            <DashboardPage />

                        </ProtectedRoute>
                    }
                />

            </Routes>

        </BrowserRouter>

    );

}

export default AppRoutes;