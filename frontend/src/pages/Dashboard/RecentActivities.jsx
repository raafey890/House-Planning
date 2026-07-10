import React from "react";

const activities = [

    "Generated Modern Villa Design",
    "Created 3BHK Floor Plan",
    "Estimated Construction Cost",
    "Saved Interior AI Concept"

];

const RecentActivities = () => {

    return (

        <div className="dashboard-card">

            <h2>Recent Activities</h2>

            <ul className="activity-list">

                {
                    activities.map((activity, index) => (

                        <li key={index}>
                            {activity}
                        </li>

                    ))
                }

            </ul>

        </div>

    );

};

export default RecentActivities;