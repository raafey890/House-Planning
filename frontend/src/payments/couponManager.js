const couponManager = {

    coupons: [

        {
            code: "WELCOME50",

            discount: 50
        },

        {
            code: "PREMIUM20",

            discount: 20
        }

    ],

    validateCoupon(code) {

        return this.coupons.find(
            coupon => coupon.code === code
        );

    },

    applyDiscount(amount, discount) {

        return amount -
        (amount * discount / 100);

    }

};

export default couponManager;