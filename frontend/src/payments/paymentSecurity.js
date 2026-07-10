const paymentSecurity = {

    secureTransaction(transaction) {

        console.log(
            "Securing Transaction"
        );

        return {

            encrypted: true,

            transaction

        };

    },

    detectFraud(transaction) {

        console.log(
            "Checking Fraud Detection"
        );

        return false;

    },

    verifyPaymentSignature(signature) {

        return signature !== "";

    }

};

export default paymentSecurity;