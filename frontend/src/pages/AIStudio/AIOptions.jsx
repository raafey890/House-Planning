import React from "react";

const options = [

    "Interior",
    "Exterior",
    "Luxury",
    "Minimal",
    "Villa",
    "Modern"

];

const AIOptions = () => {

    return (

        <div className="ai-options">

            {
                options.map((option, index) => (

                    <button
                        className="option-btn"
                        key={index}
                    >

                        {option}

                    </button>

                ))
            }

        </div>

    );

};

export default AIOptions;