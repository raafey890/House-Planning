import { useState } from "react";

function PlanGenerator() {

    const [plotSize, setPlotSize] =
    useState("");

    const [floors, setFloors] =
    useState(1);

    const [loading, setLoading] =
    useState(false);

    function generatePlan() {

        setLoading(true);

        setTimeout(() => {

            setLoading(false);

            console.log(
                "AI Floor Plan Generated"
            );

        }, 2000);

    }

    return (

        <div className="plan-generator">

            <h2>
                Generate Floor Plan
            </h2>

            <input
                type="text"
                placeholder="Enter Plot Size"
                value={plotSize}
                onChange={(event) =>
                    setPlotSize(
                        event.target.value
                    )
                }
            />

            <input
                type="number"
                value={floors}
                onChange={(event) =>
                    setFloors(
                        event.target.value
                    )
                }
            />

            <button onClick={generatePlan}>

                {

                    loading
                    ? "Generating..."
                    : "Generate Plan"

                }

            </button>

        </div>

    );

}

export default PlanGenerator;