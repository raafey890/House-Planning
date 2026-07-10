function projectSaveService(projectData) {

    console.log("Saving User Project");

    console.log(projectData);

    return {

        status: "success",

        message: "Project Saved Successfully"

    };
}

export default projectSaveService;