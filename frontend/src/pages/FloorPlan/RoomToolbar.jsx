import React from "react";

const rooms = [

    "Bedroom",
    "Kitchen",
    "Bathroom",
    "Living Room",
    "Dining Room"

];

const RoomToolbar = () => {

    return (

        <div className="room-toolbar">

            <h2>Add Rooms</h2>

            <div className="room-buttons">

                {
                    rooms.map((room, index) => (

                        <button
                            key={index}
                            className="room-btn"
                        >

                            {room}

                        </button>

                    ))
                }

            </div>

        </div>

    );

};

export default RoomToolbar;