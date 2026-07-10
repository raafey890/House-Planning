function trackingService(eventName) {

    console.log("Tracking Event:");

    console.log(eventName);

    return {

        status: "tracked",

        event: eventName

    };
}

export default trackingService;