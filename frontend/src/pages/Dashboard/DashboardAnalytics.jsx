import React from "react";

const analyticsData = [

    {
        title: "AI Designs",
        value: "128",
        growth: "+18%"
    },

    {
        title: "Floor Plans",
        value: "64",
        growth: "+10%"
    },

    {
        title: "Estimations",
        value: "42",
        growth: "+12%"
    },

    {
        title: "Saved Projects",
        value: "19",
        growth: "+7%"
    }

];

const DashboardAnalytics = () => {

    return (

        <div className="analytics-grid">

            {
                analyticsData.map((item, index) => (

                    <div
                        key={index}
                        className="analytics-card"
                    >

                        <h3>{item.title}</h3>

                        <h1>{item.value}</h1>

                        <span>{item.growth}</span>

                    </div>

                ))
            }

        </div>

    );

};

export default DashboardAnalytics;