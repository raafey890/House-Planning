import React from "react";

const DashboardHeader = () => {

    return (

        <header className="dashboard-topbar">

            <div>

                <h2>
                    Welcome Back
                </h2>

                <p>
                    Manage your AI projects
                </p>

            </div>

            <div className="dashboard-user">

                <img
                    src="https://i.pravatar.cc/100"
                    alt="user"
                />

            </div>

        </header>

    );

};

export default DashboardHeader;