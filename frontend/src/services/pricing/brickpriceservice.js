function brickPriceService(city) {

    console.log("Fetching Brick Prices");

    const brickData = {

        city: city,

        pricePerBrick: 12,

        type: "Red Clay Brick"

    };

    return brickData;
}

export default brickPriceService;