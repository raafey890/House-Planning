function recommendationEngine(userData) {

    const recommendations = [];

    if(userData.budget > 3000000) {

        recommendations.push(
            "Luxury Design Recommended"
        );

    }

    if(userData.facing === "East") {

        recommendations.push(
            "Natural Lighting Advantage"
        );

    }

    return recommendations;
}

export default recommendationEngine;