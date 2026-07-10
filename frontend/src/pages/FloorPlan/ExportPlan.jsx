function ExportPlan() {

    function exportPDF() {

        console.log(
            "Exporting Floor Plan PDF"
        );

    }

    function exportImage() {

        console.log(
            "Exporting Floor Plan Image"
        );

    }

    return (

        <div className="export-plan">

            <h2>
                Export Plan
            </h2>

            <button onClick={exportPDF}>

                Export PDF

            </button>

            <button onClick={exportImage}>

                Export Image

            </button>

        </div>

    );

}

export default ExportPlan;