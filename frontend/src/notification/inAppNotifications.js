const inAppNotifications = {

    notifications: [],

    unreadCount: 0,

    addNotification(message, type) {

        const notification = {

            id: Date.now(),

            message,

            type,

            read: false,

            createdAt: new Date()

        };

        this.notifications.unshift(
            notification
        );

        this.unreadCount++;

    },

    markAsRead(notificationId) {

        const notification =
        this.notifications.find(
            item => item.id === notificationId
        );

        if(notification && !notification.read) {

            notification.read = true;

            this.unreadCount--;

        }

    },

    clearNotifications() {

        this.notifications = [];

        this.unreadCount = 0;

    }

};

export default inAppNotifications;