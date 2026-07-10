function CostBreakdown() {

    const breakdown = [

        {
            title: "Cement",
            amount: 50000
        },

        {
            title: "Steel",
            amount: 80000
        },

        {
            title: "Labor",
            amount: 45000
        },

        {
            title: "Electrical",
            amount: 30000
        }

    ];

    return (

        <div className="cost-breakdown">

            <h2>
                Cost Breakdown
            </h2>

            {

                breakdown.map(item => (

                    <div
                        key={item.title}
                        className="breakdown-card"
                    >

                        <h3>
                            {item.title}
                        </h3>

                        <p>
                            ₹ {item.amount}
                        </p>

                    </div>

                ))

            }

        </div>

    );

}

export default CostBreakdown;