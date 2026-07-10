import PlotSelector from "./PlotSelector.jsx";
import RoomPlanner from "./RoomPlanner.jsx";
import FacingSelector from "./FacingSelector.jsx";
import BudgetPlanner from "./BudgetPlanner.jsx";

function PlannerPage() {

    return (

        <div className="planner-page">

            <h1>
                Smart House Planner
            </h1>

            <PlotSelector />

            <RoomPlanner />

            <FacingSelector />

            <BudgetPlanner />

        </div>

    );

}

export default PlannerPage;