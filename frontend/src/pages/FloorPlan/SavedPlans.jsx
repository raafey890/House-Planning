import React from "react";

const plans = [

    "Luxury Villa",
    "Modern Duplex",
    "3BHK Apartment"

];

const SavedPlans = () => {

    return (

        <div className="saved-plans">

            <h2>Saved Plans</h2>

            <div className="saved-list">

                {
                    plans.map((plan, index) => (

                        <div
                            className="saved-item"
                            key={index}
                        >

                            {plan}

                        </div>

                    ))
                }

            </div>

        </div>

    );

};

export default SavedPlans;