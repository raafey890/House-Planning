function laborCostService(area) {

    console.log("Calculating Labor Cost");

    const laborCostPerSqft = 250;

    const totalLaborCost = area * laborCostPerSqft;

    return {

        area: area,

        laborCost: totalLaborCost

    };
}

export default laborCostService;