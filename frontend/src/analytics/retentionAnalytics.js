const retentionAnalytics = {

    returningUsers: 0,

    dailyActiveUsers: 0,

    weeklyActiveUsers: 0,

    monthlyActiveUsers: 0,

    increaseReturningUsers() {

        this.returningUsers++;

    },

    updateDailyActiveUsers(count) {

        this.dailyActiveUsers = count;

    },

    calculateRetentionRate(
        retainedUsers,
        totalUsers
    ) {

        return (
            retainedUsers /
            totalUsers
        ) * 100;

    }

};

export default retentionAnalytics;