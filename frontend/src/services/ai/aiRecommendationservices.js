function aiRecommendationService(userData) {

    const recommendations = [];

    if(userData.facing === "East") {

        recommendations.push(
            "East-facing homes improve morning lighting."
        );

    }

    if(userData.budget > 3000000) {

        recommendations.push(
            "Luxury elevation recommended for this budget."
        );

    }

    recommendations.push(
        "Suggested balcony placement near living room."
    );

    return recommendations;
}

export default aiRecommendationService;