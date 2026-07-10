const reminderNotifications = {

    reminders: [],

    addReminder(task, time) {

        const reminder = {

            id: Date.now(),

            task,

            time,

            completed: false

        };

        this.reminders.push(reminder);

    },

    completeReminder(reminderId) {

        const reminder =
        this.reminders.find(
            item => item.id === reminderId
        );

        if(reminder) {

            reminder.completed = true;

        }

    },

    getPendingReminders() {

        return this.reminders.filter(
            reminder => !reminder.completed
        );

    }

};

export default reminderNotifications;