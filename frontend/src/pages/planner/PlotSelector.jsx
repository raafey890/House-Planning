import { useState } from "react";

function PlotSelector() {

    const [plotSize, setPlotSize] =
    useState("");

    return (

        <div className="plot-selector">

            <h2>
                Select Plot Size
            </h2>

            <input
                type="text"
                placeholder="30x40"
                value={plotSize}
                onChange={(event) =>
                    setPlotSize(
                        event.target.value
                    )
                }
            />

            <p>
                Selected Plot:
                {plotSize}
            </p>

        </div>

    );

}

export default PlotSelector;