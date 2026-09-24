import { usePlannerStore } from "../../store";

function RoomPlanner() {
    const {
        bedrooms, bathrooms, kitchens, livingRooms, balconies, 
        poojaRoom, setField
    } = usePlannerStore();

    return (
        <div className="room-planner">
            <h2>Room Requirements</h2>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <label>
                    Bedrooms:
                    <input type="number" value={bedrooms} onChange={(e) => setField('bedrooms', Number(e.target.value))} min="1" />
                </label>
                <label>
                    Bathrooms:
                    <input type="number" value={bathrooms} onChange={(e) => setField('bathrooms', Number(e.target.value))} min="1" />
                </label>
                <label>
                    Kitchens:
                    <input type="number" value={kitchens} onChange={(e) => setField('kitchens', Number(e.target.value))} min="1" />
                </label>
                <label>
                    Living Rooms:
                    <input type="number" value={livingRooms} onChange={(e) => setField('livingRooms', Number(e.target.value))} min="1" />
                </label>
                <label>
                    Balconies:
                    <input type="number" value={balconies} onChange={(e) => setField('balconies', Number(e.target.value))} min="0" />
                </label>
                <label>
                    <input type="checkbox" checked={poojaRoom} onChange={(e) => setField('poojaRoom', e.target.checked)} />
                    Pooja Room
                </label>
            </div>
        </div>
    );
}

export default RoomPlanner;