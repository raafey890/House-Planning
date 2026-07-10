import PlanGenerator from "./PlanGenerator.jsx";
import PlanPreview from "./PlanPreview.jsx";
import ExportPlan from "./ExportPlan.jsx";

function FloorPlanPage() {

    return (

        <div className="floorplan-page">

            <h1>
                AI Floor Plan Generator
            </h1>

            <PlanGenerator />

            <PlanPreview />

            <ExportPlan />

        </div>

    );

}

export default FloorPlanPage;