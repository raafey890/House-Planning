const NotificationContext = {

    notifications: [],

    unreadCount: 0,

    soundEnabled: true,

    pushEnabled: true,

    addNotification(message, type) {

        const notification = {

            message,
            type,
            time: new Date()

        };

        this.notifications.push(notification);

        this.unreadCount++;

    },

    markAllAsRead() {

        this.unreadCount = 0;

    },

    clearNotifications() {

        this.notifications = [];

        this.unreadCount = 0;

    },

    toggleSound() {

        this.soundEnabled =
        !this.soundEnabled;

    },

    togglePushNotifications() {

        this.pushEnabled =
        !this.pushEnabled;

    }

};

export default NotificationContext;