async function uploadService(file) {

    console.log("Uploading File...");

    console.log(file);

    return {

        status: "success",

        message: "File Uploaded Successfully"

    };
}

export default uploadService;