function smsService(phoneNumber, message) {

    console.log("Sending SMS");

    console.log(phoneNumber);

    console.log(message);

    return {

        status: "success",

        message: "SMS Delivered"

    };
}

export default smsService;