function steelPriceService(city) {

    console.log("Fetching Steel Prices");

    const steelData = {

        city: city,

        pricePerKG: 72,

        brand: "TATA Steel"

    };

    return steelData;
}

export default steelPriceService;   