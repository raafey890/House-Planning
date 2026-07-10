import React from "react";

import DashboardAnalytics from "./DashboardAnalytics";
import RecentActivities from "./RecentActivities";
import UserProjects from "./UserProjects";

import "../../styles/pages/dashboard.css";

const DashboardPage = () => {

    return (

        <div className="dashboard-page">

            <div className="dashboard-header">

                <div>
                    <h1>AI House Planning Dashboard</h1>
                    <p>
                        Manage your projects, AI generations,
                        floor plans and estimations.
                    </p>
                </div>

                <button className="dashboard-btn">
                    + New Project
                </button>

            </div>

            <DashboardAnalytics />

            <div className="dashboard-grid">

                <UserProjects />

                <RecentActivities />

            </div>

        </div>

    );

};

export default DashboardPage;