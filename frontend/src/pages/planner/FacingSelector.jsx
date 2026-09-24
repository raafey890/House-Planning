import { usePlannerStore } from "../../store";

function FacingSelector() {
    const { facing, setField } = usePlannerStore();

    return (
        <div className="facing-selector">
            <h2>Facing Direction</h2>
            <select
                value={facing}
                onChange={(e) => setField('facing', e.target.value)}
            >
                <option value="East">East</option>
                <option value="West">West</option>
                <option value="North">North</option>
                <option value="South">South</option>
            </select>
            <p>Selected Facing: {facing}</p>
        </div>
    );
}

export default FacingSelector;