const pushNotifications = {

    enabled: true,

    subscribers: [],

    sentNotifications: [],

    subscribeUser(userId) {

        if(!this.subscribers.includes(userId)) {

            this.subscribers.push(userId);

        }

    },

    unsubscribeUser(userId) {

        this.subscribers =
        this.subscribers.filter(
            id => id !== userId
        );

    },

    sendNotification(title, message) {

        const notification = {

            title,

            message,

            createdAt: new Date()

        };

        this.sentNotifications.push(
            notification
        );

        console.log(
            `Push Notification Sent: ${title}`
        );

    },

    toggleNotifications(status) {

        this.enabled = status;

    }

};

export default pushNotifications;