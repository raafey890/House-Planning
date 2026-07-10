const billingHistory = {

    records: [],

    addRecord(record) {

        this.records.push(record);

    },

    getUserHistory(userId) {

        return this.records.filter(
            record => record.userId === userId
        );

    },

    exportBillingHistory() {

        console.log(
            "Exporting Billing History"
        );

    }

};

export default billingHistory;