async function emailService(email, subject) {

    console.log("Sending Email");

    console.log(email);

    console.log(subject);

    return {

        status: "success",

        message: "Email Sent Successfully"

    };
}

export default emailService;