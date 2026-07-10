function cementPriceService(city) {

    console.log("Fetching Cement Prices");

    const cementData = {

        city: city,

        pricePerBag: 420,

        brand: "UltraTech Cement"

    };

    return cementData;
}

export default cementPriceService;