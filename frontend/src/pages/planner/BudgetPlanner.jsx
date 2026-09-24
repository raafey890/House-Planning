import { usePlannerStore } from "../../store";

function BudgetPlanner() {
    const { budget, setField } = usePlannerStore();

    return (
        <div className="budget-planner">
            <h2>Budget Planner</h2>
            <input
                type="number"
                placeholder="Enter Budget"
                value={budget}
                onChange={(e) => setField('budget', Number(e.target.value))}
            />
            <p>Estimated Budget: ₹ {budget}</p>
        </div>
    );
}

export default BudgetPlanner;