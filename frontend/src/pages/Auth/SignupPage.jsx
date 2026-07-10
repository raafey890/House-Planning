import { useState } from "react";

function SignupPage() {

    const [username, setUsername] =
    useState("");

    const [email, setEmail] =
    useState("");

    const [password, setPassword] =
    useState("");

    function handleSignup(event) {

        event.preventDefault();

        console.log(
            "User Signup:",
            username
        );

    }

    return (

        <div className="signup-page">

            <h1>
                Create Account
            </h1>

            <form onSubmit={handleSignup}>

                <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(event) =>
                        setUsername(
                            event.target.value
                        )
                    }
                />

                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(event) =>
                        setEmail(
                            event.target.value
                        )
                    }
                />

                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(event) =>
                        setPassword(
                            event.target.value
                        )
                    }
                />

                <button type="submit">

                    Signup

                </button>

            </form>

        </div>

    );

}

export default SignupPage;