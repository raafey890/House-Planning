import React from "react";

const projects = [

    {
        name: "Luxury Villa",
        status: "Completed"
    },

    {
        name: "Modern Apartment",
        status: "In Progress"
    },

    {
        name: "Farm House",
        status: "Draft"
    }

];

const UserProjects = () => {

    return (

        <div className="dashboard-card">

            <h2>User Projects</h2>

            <div className="projects-list">

                {
                    projects.map((project, index) => (

                        <div
                            key={index}
                            className="project-item"
                        >

                            <div>

                                <h3>{project.name}</h3>

                                <p>{project.status}</p>

                            </div>

                            <button>
                                Open
                            </button>

                        </div>

                    ))
                }

            </div>

        </div>

    );

};

export default UserProjects;