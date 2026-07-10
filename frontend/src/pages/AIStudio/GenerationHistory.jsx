import React from "react";

const history = [

    {
        title: "Luxury Exterior",
        date: "2 mins ago"
    },

    {
        title: "Modern Interior",
        date: "10 mins ago"
    },

    {
        title: "3BHK Floor Plan",
        date: "25 mins ago"
    }

];

const GenerationHistory = () => {

    return (

        <div className="generation-history">

            <h2>
                Generation History
            </h2>

            <div className="generation-list">

                {
                    history.map((item, index) => (

                        <div
                            className="generation-item"
                            key={index}
                        >

                            <div>

                                <h3>{item.title}</h3>

                                <p>{item.date}</p>

                            </div>

                            <button className="primary-btn">

                                View

                            </button>

                        </div>

                    ))
                }

            </div>

        </div>

    );

};

export default GenerationHistory;