import { usePlannerStore } from "../../store";

function PlotSelector() {
    const plotLength = usePlannerStore((state) => state.plotLength);
    const plotWidth = usePlannerStore((state) => state.plotWidth);
    const setField = usePlannerStore((state) => state.setField);

    return (
        <div className="plot-selector">
            <h2>Plot Details</h2>
            <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                <label>
                    Length (ft):
                    <input
                        type="number"
                        placeholder="30"
                        value={plotLength}
                        onChange={(e) => setField('plotLength', Number(e.target.value))}
                        style={{ marginLeft: '10px', width: '80px' }}
                    />
                </label>
                <span>x</span>
                <label>
                    Width (ft):
                    <input
                        type="number"
                        placeholder="40"
                        value={plotWidth}
                        onChange={(e) => setField('plotWidth', Number(e.target.value))}
                        style={{ marginLeft: '10px', width: '80px' }}
                    />
                </label>
            </div>
            <p>Total Area: {plotLength * plotWidth} sq ft</p>
        </div>
    );
}

export default PlotSelector;