async function signupService(userData) {

    console.log("Creating User Account");

    console.log(userData);

    const response = {

        status: "success",

        message: "Account Created Successfully"

    };

    return response;
}

export default signupService;