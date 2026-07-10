function materialEstimator(area) {

    return {

        cementBags: area * 0.25,

        bricks: area * 8,

        steelKG: area * 3

    };
}

export default materialEstimator;