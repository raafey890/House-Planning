async function loginService(email, password) {

    console.log("User Login Request");

    console.log(email);

    const response = {

        status: "success",

        message: "Login Successful",

        user: {

            name: "Raafey",
            email: email

        }

    };

    return response;
}

export default loginService;