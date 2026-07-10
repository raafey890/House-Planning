import { useState } from "react";

function FilterPanel() {

    const [search, setSearch] =
    useState("");

    return (

        <div className="filter-panel">

            <input
                type="text"
                placeholder="Search Designs"
                value={search}
                onChange={(event) =>
                    setSearch(
                        event.target.value
                    )
                }
            />

            <select>

                <option>
                    Modern
                </option>

                <option>
                    Luxury
                </option>

                <option>
                    Minimal
                </option>

                <option>
                    Traditional
                </option>

            </select>

        </div>

    );

}

export default FilterPanel;