const roomCalculator = (
  length,
  width
) => {
  const area = length * width;

  return {
    length,
    width,
    area,
    unit: "sq.ft",
  };
};

module.exports = roomCalculator;