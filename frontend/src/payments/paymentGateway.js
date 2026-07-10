const paymentGateway = {

    supportedGateways: [

        "Razorpay",
        "Stripe",
        "PayPal"

    ],

    currentGateway: "Razorpay",

    initializePayment(amount) {

        console.log(
            `Initializing Payment: ₹${amount}`
        );

        return {

            status: "initialized",

            amount

        };

    },

    verifyPayment(transactionId) {

        console.log(
            `Verifying Transaction ${transactionId}`
        );

        return {

            verified: true

        };

    },

    refundPayment(transactionId) {

        console.log(
            `Refund Started For ${transactionId}`
        );

        return {

            refunded: true

        };

    }

};

export default paymentGateway;