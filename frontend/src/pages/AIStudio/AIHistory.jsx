import React from "react";

const history = [

    "Luxury Villa Exterior",
    "Minimal Interior Design",
    "3BHK Floor Plan",
    "Modern Glass House"

];

const AIHistory = () => {

    return (

        <div className="ai-history">

            <h2>Recent AI Prompts</h2>

            <div className="history-list">

                {
                    history.map((item, index) => (

                        <div
                            className="history-item"
                            key={index}
                        >

                            {item}

                        </div>

                    ))
                }

            </div>

        </div>

    );

};

export default AIHistory;