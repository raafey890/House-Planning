const dashboardAnalytics = {

    dashboardViews: 0,

    mostVisitedPage: "Home",

    topFeatures: [],

    increaseDashboardViews() {

        this.dashboardViews++;

    },

    addTopFeature(featureName) {

        this.topFeatures.push(featureName);

    },

    getTopFeature() {

        return this.topFeatures[0];

    }

};

export default dashboardAnalytics;