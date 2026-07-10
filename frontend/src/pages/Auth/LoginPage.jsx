import { useState } from "react";

function LoginPage() {

    const [email, setEmail] =
    useState("");

    const [password, setPassword] =
    useState("");

    function handleLogin(event) {

        event.preventDefault();

        console.log(
            "User Login:",
            email
        );

    }

    return (

        <div className="login-page">

            <h1>
                Login
            </h1>

            <form onSubmit={handleLogin}>

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

                <input
                    type="password"
                    placeholder="Enter Password"
                    value={password}
                    onChange={(event) =>
                        setPassword(
                            event.target.value
                        )
                    }
                />

                <button type="submit">

                    Login

                </button>

            </form>

        </div>

    );

}

export default LoginPage;