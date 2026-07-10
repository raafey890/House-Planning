const plans = [

    {
        id: 1,
        name: "Basic",
        price: "₹499",
        features: [
            "5 AI Designs",
            "Basic Floor Plans",
            "Standard Support"
        ]
    },

    {
        id: 2,
        name: "Pro",
        price: "₹1499",
        features: [
            "Unlimited AI Designs",
            "3D Floor Plans",
            "Priority Support"
        ]
    },

    {
        id: 3,
        name: "Enterprise",
        price: "₹4999",
        features: [
            "Team Collaboration",
            "Advanced Analytics",
            "Dedicated Manager"
        ]
    }

];

function SubscriptionPlans() {

    return (

        <div className="subscription-plans">

            <h2>
                Subscription Plans
            </h2>

            <div className="plans-grid">

                {

                    plans.map(plan => (

                        <div
                            key={plan.id}
                            className="plan-card"
                        >

                            <h3>
                                {plan.name}
                            </h3>

                            <h2>
                                {plan.price}
                            </h2>

                            <ul>

                                {

                                    plan.features.map(
                                        feature => (

                                            <li
                                                key={feature}
                                            >

                                                {feature}

                                            </li>

                                        )
                                    )

                                }

                            </ul>

                            <button>
                                Choose Plan
                            </button>

                        </div>

                    ))

                }

            </div>

        </div>

    );

}

export default SubscriptionPlans;