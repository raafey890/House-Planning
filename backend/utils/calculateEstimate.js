const calculateEstimate = (
  area,
  costPerSqFt = 2000
) => {
  const totalCost = area * costPerSqFt;

  return {
    area,
    costPerSqFt,
    totalCost,
  };
};

module.exports = calculateEstimate;