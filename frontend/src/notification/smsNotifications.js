const smsNotifications = {

    sentMessages: [],

    sendSMS(phoneNumber, message) {

        const sms = {

            phoneNumber,

            message,

            sentAt: new Date()

        };

        this.sentMessages.push(sms);

        console.log(
            `SMS Sent To ${phoneNumber}`
        );

    },

    sendOTP(phoneNumber) {

        const otp =
        Math.floor(
            100000 + Math.random() * 900000
        );

        console.log(
            `OTP ${otp} sent to ${phoneNumber}`
        );

        return otp;

    }

};

export default smsNotifications;