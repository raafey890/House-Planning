const revenueAnalytics = {

    totalRevenue: 0,

    monthlyRevenue: {},

    subscriptionsSold: 0,

    addRevenue(amount, month) {

        this.totalRevenue += amount;

        if(!this.monthlyRevenue[month]) {

            this.monthlyRevenue[month] = 0;

        }

        this.monthlyRevenue[month] += amount;

    },

    sellSubscription() {

        this.subscriptionsSold++;

    },

    getMonthlyRevenue(month) {

        return this.monthlyRevenue[month] || 0;

    }

};

export default revenueAnalytics;