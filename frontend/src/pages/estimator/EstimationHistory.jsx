import React from "react";

const history = [

    "Luxury Villa Estimate",
    "Modern Duplex Estimate",
    "Farm House Budget"

];

const EstimationHistory = () => {

    return (

        <div className="estimation-history">

            <h2>Recent Estimations</h2>

            <div className="history-list">

                {
                    history.map((item, index) => (

                        <div
                            className="history-card"
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

export default EstimationHistory;