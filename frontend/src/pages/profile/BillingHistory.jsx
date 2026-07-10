const billingHistory = [

    {
        id: 1,
        plan: "Pro Plan",
        amount: "₹1499",
        date: "12 May 2026"
    },

    {
        id: 2,
        plan: "Enterprise Plan",
        amount: "₹4999",
        date: "25 June 2026"
    }

];

function BillingHistory() {

    return (

        <div className="billing-history">

            <h2>
                Billing History
            </h2>

            {

                billingHistory.map(item => (

                    <div
                        key={item.id}
                        className="billing-card"
                    >

                        <h3>
                            {item.plan}
                        </h3>

                        <p>
                            {item.amount}
                        </p>

                        <p>
                            {item.date}
                        </p>

                    </div>

                ))

            }

        </div>

    );

}

export default BillingHistory;