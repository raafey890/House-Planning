import React from "react";

const stats = [

    {
        title: "Projects",
        value: "24"
    },

    {
        title: "AI Designs",
        value: "128"
    },

    {
        title: "Estimations",
        value: "42"
    },

    {
        title: "Saved Plans",
        value: "16"
    }

];

const DashboardStats = () => {

    return (

        <div className="dashboard-stats-grid">

            {
                stats.map((item, index) => (

                    <div
                        className="stats-card"
                        key={index}
                    >

                        <h3>{item.title}</h3>

                        <h1>{item.value}</h1>

                    </div>

                ))
            }

        </div>

    );

};

export default DashboardStats;