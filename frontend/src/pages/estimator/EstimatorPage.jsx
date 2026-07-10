import MaterialEstimator from "./MaterialEstimator.jsx";
import LaborEstimator from "./LaborEstimator.jsx";
import CostBreakdown from "./CostBreakdown.jsx";

function EstimatorPage() {

    return (

        <div className="estimator-page">

            <h1>
                Construction Cost Estimator
            </h1>

            <MaterialEstimator />

            <LaborEstimator />

            <CostBreakdown />

        </div>

    );

}

export default EstimatorPage;