const transactionManager = {

    transactions: [],

    addTransaction(transaction) {

        this.transactions.push(transaction);

    },

    getTransaction(transactionId) {

        return this.transactions.find(
            transaction =>
            transaction.id === transactionId
        );

    },

    getAllTransactions() {

        return this.transactions;

    },

    calculateRevenue() {

        return this.transactions.reduce(
            (total, transaction) =>
            total + transaction.amount,
            0
        );

    }

};

export default transactionManager;