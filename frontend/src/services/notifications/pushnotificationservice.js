function pushNotificationService(message) {

    console.log("Push Notification:");

    console.log(message);

    return {

        status: "success",

        notification: message

    };
}

export default pushNotificationService;