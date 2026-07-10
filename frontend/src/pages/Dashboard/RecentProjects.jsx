import React from "react";

const projects = [

    {
        name: "Luxury Villa",
        status: "Completed"
    },

    {
        name: "Modern House",
        status: "In Progress"
    },

    {
        name: "Farm House",
        status: "Draft"
    }

];

const RecentProjects = () => {

    return (

        <div className="dashboard-card">

            <h2>Recent Projects</h2>

            <div className="recent-projects">

                {
                    projects.map((project, index) => (

                        <div
                            className="project-row"
                            key={index}
                        >

                            <div>

                                <h3>{project.name}</h3>

                                <p>{project.status}</p>

                            </div>

                            <button className="primary-btn">

                                Open

                            </button>

                        </div>

                    ))
                }

            </div>

        </div>

    );

};

export default RecentProjects;