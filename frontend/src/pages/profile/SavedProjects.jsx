const projects = [

    {
        id: 1,
        title: "Modern Duplex"
    },

    {
        id: 2,
        title: "Luxury Villa"
    },

    {
        id: 3,
        title: "Minimal House"
    }

];

function SavedProjects() {

    return (

        <div className="saved-projects">

            <h2>
                Saved Projects
            </h2>

            <div className="projects-grid">

                {

                    projects.map(project => (

                        <div
                            key={project.id}
                            className="project-card"
                        >

                            <h3>
                                {project.title}
                            </h3>

                            <button>
                                Open Project
                            </button>

                        </div>

                    ))

                }

            </div>

        </div>

    );

}

export default SavedProjects;