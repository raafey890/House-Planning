const notificationHistory = {

    history: [],

    addHistory(notification) {

        this.history.push({

            ...notification,

            deliveredAt: new Date()

        });

    },

    getHistory() {

        return this.history;

    },

    clearHistory() {

        this.history = [];

    }

};

export default notificationHistory;