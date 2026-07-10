const notificationPreferences = {

    pushEnabled: true,

    emailEnabled: true,

    smsEnabled: false,

    marketingNotifications: true,

    AIUpdates: true,

    securityAlerts: true,

    updatePreference(setting, value) {

        if(this.hasOwnProperty(setting)) {

            this[setting] = value;

        }

    },

    getPreferences() {

        return {

            pushEnabled: this.pushEnabled,

            emailEnabled: this.emailEnabled,

            smsEnabled: this.smsEnabled

        };

    }

};

export default notificationPreferences;