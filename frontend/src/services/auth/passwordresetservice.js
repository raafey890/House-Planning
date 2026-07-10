async function passwordResetService(email) {

    console.log("Password Reset Request");

    console.log(email);

    return {

        status: "success",

        message: "Reset Link Sent To Email"

    };
}

export default passwordResetService;