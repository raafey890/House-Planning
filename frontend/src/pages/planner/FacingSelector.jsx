import { useState } from "react";

function FacingSelector() {

    const [facing, setFacing] =
    useState("East");

    return (

        <div className="facing-selector">

            <h2>
                Facing Direction
            </h2>

            <select
                value={facing}
                onChange={(event) =>
                    setFacing(
                        event.target.value
                    )
                }
            >

                <option>
                    East
                </option>

                <option>
                    West
                </option>

                <option>
                    North
                </option>

                <option>
                    South
                </option>

            </select>

            <p>
                Selected Facing:
                {facing}
            </p>

        </div>

    );

}

export default FacingSelector;