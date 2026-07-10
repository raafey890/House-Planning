function paintPriceService(city) {

    console.log("Fetching Paint Prices");

    const paintData = {

        city: city,

        pricePerLiter: 340,

        brand: "Asian Paints"

    };

    return paintData;
}

export default paintPriceService;