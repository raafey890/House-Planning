const notificationScheduler = {

    scheduledNotifications: [],

    scheduleNotification(
        title,
        message,
        sendTime
    ) {

        const notification = {

            id: Date.now(),

            title,

            message,

            sendTime,

            scheduled: true

        };

        this.scheduledNotifications.push(
            notification
        );

    },

    cancelScheduledNotification(id) {

        this.scheduledNotifications =
        this.scheduledNotifications.filter(
            item => item.id !== id
        );

    },

    getUpcomingNotifications() {

        return this.scheduledNotifications;

    }

};

export default notificationScheduler;