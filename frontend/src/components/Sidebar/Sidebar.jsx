import "./Sidebar.css";

import SidebarItem from "./SidebarItem";

function Sidebar() {

    const menuItems = [

        {
            title: "Dashboard",
            path: "/dashboard"
        },

        {
            title: "Planner",
            path: "/planner"
        },

        {
            title: "Analytics",
            path: "/analytics"
        },

        {
            title: "Marketplace",
            path: "/marketplace"
        },

        {
            title: "Premium",
            path: "/premium"
        },

        {
            title: "Settings",
            path: "/settings"
        }

    ];

    return (

        <aside className="sidebar">

            <div className="sidebar-logo">

                <h2>
                    AI Planner
                </h2>

            </div>

            <div className="sidebar-menu">

                {menuItems.map((item, index) => (

                    <SidebarItem
                        key={index}
                        title={item.title}
                        path={item.path}
                    />

                ))}

            </div>

        </aside>

    );

}

export default Sidebar;