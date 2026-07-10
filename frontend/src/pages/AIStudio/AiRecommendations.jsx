import React from "react";

const recommendations = [

    "Luxury Villa Exterior",
    "Modern Duplex Design",
    "Minimal Interior Concept",
    "Smart Glass House",
    "Japanese Style Home"

];

const AIRecommendations = () => {

    return (

        <div className="ai-recommendations">

            <h2>
                AI Recommendations
            </h2>

            <div className="recommendation-grid">

                {
                    recommendations.map((item, index) => (

                        <div
                            className="recommendation-card"
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

export default AIRecommendations;