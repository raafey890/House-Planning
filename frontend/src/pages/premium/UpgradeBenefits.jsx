const benefits = [

    "Unlimited AI Generations",

    "High Resolution Exports",

    "Priority AI Processing",

    "Advanced Floor Planning",

    "Cloud Project Backup",

    "Premium Marketplace Access"

];

function UpgradeBenefits() {

    return (

        <div className="upgrade-benefits">

            <h2>
                Premium Benefits
            </h2>

            <div className="benefits-grid">

                {

                    benefits.map(item => (

                        <div
                            key={item}
                            className="benefit-card"
                        >

                            <p>
                                {item}
                            </p>

                        </div>

                    ))

                }

            </div>

        </div>

    );

}

export default UpgradeBenefits;