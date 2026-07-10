const marketplaceAnalytics = {

    totalBookings: 0,

    totalRevenue: 0,

    topServices: [],

    increaseBookings() {

        this.totalBookings++;

    },

    addRevenue(amount) {

        this.totalRevenue += amount;

    },

    addTopService(serviceName) {

        this.topServices.push(serviceName);

    },

    getMarketplaceStats() {

        return {

            totalBookings:
            this.totalBookings,

            totalRevenue:
            this.totalRevenue,

            topServices:
            this.topServices

        };

    }

};

export default marketplaceAnalytics;