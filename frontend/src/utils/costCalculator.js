function costCalculator(materials) {

    let total = 0;

    materials.forEach(item => {

        total += item.price;

    });

    return total;
}

export default costCalculator;