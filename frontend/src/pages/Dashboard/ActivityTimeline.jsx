import React from "react";

const activities = [

    "Generated AI Interior",
    "Created Floor Plan",
    "Saved Luxury Villa",
    "Calculated Estimation"

];

const ActivityTimeline = () => {

    return (

        <div className="dashboard-card">

            <h2>Activity Timeline</h2>

            <div className="timeline-list">

                {
                    activities.map((activity, index) => (

                        <div
                            className="timeline-item"
                            key={index}
                        >

                            <div className="timeline-dot"></div>

                            <p>{activity}</p>

                        </div>

                    ))
                }

            </div>

        </div>

    );

};

export default ActivityTimeline;