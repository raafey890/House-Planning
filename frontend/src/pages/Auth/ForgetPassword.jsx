import { useState } from "react";

function ForgotPassword() {

    const [email, setEmail] =
    useState("");

    function handleReset(event) {

        event.preventDefault();

        console.log(
            "Password Reset:",
            email
        );

    }

    return (

        <div className="forgot-password">

            <h1>
                Forgot Password
            </h1>

            <form onSubmit={handleReset}>

                <input
                    type="email"
                    placeholder="Enter Email"
                    value={email}
                    onChange={(event) =>
                        setEmail(
                            event.target.value
                        )
                    }
                />

                <button type="submit">

                    Reset Password

                </button>

            </form>

        </div>

    );

}

export default ForgotPassword;