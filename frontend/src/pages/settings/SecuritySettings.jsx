import { useState } from "react";

function SecuritySettings() {

    const [twoFactor,
    setTwoFactor] =
    useState(false);

    function handlePasswordReset() {

        console.log(
            "Password Reset Requested"
        );

    }

    return (

        <div className="security-settings">

            <h2>
                Security Settings
            </h2>

            <label>

                <input
                    type="checkbox"
                    checked={twoFactor}
                    onChange={() =>
                        setTwoFactor(
                            !twoFactor
                        )
                    }
                />

                Enable 2FA

            </label>

            <button
                onClick={handlePasswordReset}
            >

                Reset Password

            </button>

        </div>

    );

}

export default SecuritySettings;