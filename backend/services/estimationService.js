const calculateCost = (
    area,
    constructionType = "standard"
) => {

    const rates = {
        basic: 1500,
        standard: 2200,
        premium: 3500
    };

    const rate =
        rates[constructionType] ||
        rates.standard;

    const totalCost = area * rate;

    return {
        area,
        constructionType,
        ratePerSqFt: rate,
        totalCost
    };
};

module.exports = {
    calculateCost
};