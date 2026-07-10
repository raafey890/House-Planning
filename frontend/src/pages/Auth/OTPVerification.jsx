import { useState } from "react";

function OTPVerification() {

    const [otp, setOTP] =
    useState("");

    function verifyOTP(event) {

        event.preventDefault();

        console.log(
            "OTP Verified:",
            otp
        );

    }

    return (

        <div className="otp-verification">

            <h1>
                OTP Verification
            </h1>

            <form onSubmit={verifyOTP}>

                <input
                    type="number"
                    placeholder="Enter OTP"
                    value={otp}
                    onChange={(event) =>
                        setOTP(
                            event.target.value
                        )
                    }
                />

                <button type="submit">

                    Verify OTP

                </button>

            </form>

        </div>

    );

}

export default OTPVerification;