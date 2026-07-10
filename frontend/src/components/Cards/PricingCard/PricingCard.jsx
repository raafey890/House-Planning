import "./PricingCard.css";

function PricingCard({
    title,
    price,
    features = []
}) {

    return (

        <div className="pricing-card">

            <h2>
                {title}
            </h2>

            <h1>
                ₹{price}
            </h1>

            <ul>

                {features.map((feature, index) => (

                    <li key={index}>

                        {feature}

                    </li>

                ))}

            </ul>

            <button>
                Choose Plan
            </button>

        </div>

    );

}

export default PricingCard;