function inAppNotificationService(notification) {

    console.log("In-App Notification");

    console.log(notification);

    return {

        status: "success",

        notification: notification

    };
}

export default inAppNotificationService;