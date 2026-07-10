function pdfGenerator(projectData) {

    console.log("Generating PDF");

    console.log(projectData);

    return {

        status: "success",

        file: "house_report.pdf"

    };
}

export default pdfGenerator;