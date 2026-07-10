import { useState } from "react";

function RoomPlanner() {

    const [bedrooms, setBedrooms] =
    useState(2);

    const [bathrooms, setBathrooms] =
    useState(1);

    return (

        <div className="room-planner">

            <h2>
                Room Planner
            </h2>

            <label>
                Bedrooms
            </label>

            <input
                type="number"
                value={bedrooms}
                onChange={(event) =>
                    setBedrooms(
                        event.target.value
                    )
                }
            />

            <label>
                Bathrooms
            </label>

            <input
                type="number"
                value={bathrooms}
                onChange={(event) =>
                    setBathrooms(
                        event.target.value
                    )
                }
            />

        </div>

    );

}

export default RoomPlanner;