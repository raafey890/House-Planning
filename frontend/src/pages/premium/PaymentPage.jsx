import { useState } from "react";

function PaymentPage() {

    const [selectedPlan, setSelectedPlan] =
    useState("Pro");

    function handlePayment() {

        console.log(
            `Processing ${selectedPlan} Plan`
        );

    }

    return (

        <div className="payment-page">

            <h2>
                Payment Gateway
            </h2>

            <select
                value={selectedPlan}
                onChange={(event) =>
                    setSelectedPlan(
                        event.target.value
                    )
                }
            >

                <option>
                    Basic
                </option>

                <option>
                    Pro
                </option>

                <option>
                    Enterprise
                </option>

            </select>

            <button onClick={handlePayment}>

                Proceed Payment

            </button>

        </div>

    );

}

export default PaymentPage;