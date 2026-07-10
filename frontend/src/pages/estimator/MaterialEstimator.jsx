import { useState } from "react";

function MaterialEstimator() {

    const [cementBags, setCementBags] =
    useState(0);

    const [steelKG, setSteelKG] =
    useState(0);

    const cementPrice = 420;

    const steelPrice = 72;

    const totalCost =

        (cementBags * cementPrice) +

        (steelKG * steelPrice);

    return (

        <div className="material-estimator">

            <h2>
                Material Estimation
            </h2>

            <input
                type="number"
                placeholder="Cement Bags"
                value={cementBags}
                onChange={(event) =>
                    setCementBags(
                        event.target.value
                    )
                }
            />

            <input
                type="number"
                placeholder="Steel KG"
                value={steelKG}
                onChange={(event) =>
                    setSteelKG(
                        event.target.value
                    )
                }
            />

            <h3>
                Material Cost:
                ₹ {totalCost}
            </h3>

        </div>

    );

}

export default MaterialEstimator;