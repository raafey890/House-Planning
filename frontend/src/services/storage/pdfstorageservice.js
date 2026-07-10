function pdfStorageService(pdfFile) {

    console.log("Saving PDF Report");

    console.log(pdfFile);

    return {

        status: "success",

        message: "PDF Stored Successfully"

    };
}

export default pdfStorageService;