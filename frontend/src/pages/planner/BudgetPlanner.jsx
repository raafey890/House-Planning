import { useState } from "react";

function BudgetPlanner() {

    const [budget, setBudget] =
    useState("");

    return (

        <div className="budget-planner">

            <h2>
                Budget Planner
            </h2>

            <input
                type="number"
                placeholder="Enter Budget"
                value={budget}
                onChange={(event) =>
                    setBudget(
                        event.target.value
                    )
                }
            />

            <p>
                Estimated Budget:
                ₹ {budget}
            </p>

        </div>

    );

}

export default BudgetPlanner;