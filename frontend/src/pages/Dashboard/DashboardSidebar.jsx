import React from "react";

const menuItems = [

    "Dashboard",
    "AI Studio",
    "Projects",
    "Estimator",
    "Gallery",
    "Settings"

];

const DashboardSidebar = () => {

    return (

        <aside className="dashboard-sidebar">

            <div className="sidebar-logo">

                AI House Planner

            </div>

            <ul className="sidebar-menu">

                {
                    menuItems.map((item, index) => (

                        <li key={index}>

                            {item}

                        </li>

                    ))
                }

            </ul>

        </aside>

    );

};

export default DashboardSidebar;