function areaConverter(length, width) {

    const area = length * width;

    return {

        sqft: area,

        sqm: area * 0.092903

    };
}

export default areaConverter;