async function cloudStorageService(data) {

    console.log("Sending Data To Cloud Storage");

    console.log(data);

    return {

        status: "success",

        message: "Cloud Backup Completed"

    };
}

export default cloudStorageService;