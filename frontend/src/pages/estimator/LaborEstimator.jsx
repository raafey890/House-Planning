import { useState } from "react";

function LaborEstimator() {

    const [workers, setWorkers] =
    useState(0);

    const [days, setDays] =
    useState(0);

    const laborPerDay = 900;

    const totalLaborCost =

        workers * days * laborPerDay;

    return (

        <div className="labor-estimator">

            <h2>
                Labor Estimation
            </h2>

            <input
                type="number"
                placeholder="Workers"
                value={workers}
                onChange={(event) =>
                    setWorkers(
                        event.target.value
                    )
                }
            />

            <input
                type="number"
                placeholder="Days"
                value={days}
                onChange={(event) =>
                    setDays(
                        event.target.value
                    )
                }
            />

            <h3>
                Labor Cost:
                ₹ {totalLaborCost}
            </h3>

        </div>

    );

}

export default LaborEstimator;