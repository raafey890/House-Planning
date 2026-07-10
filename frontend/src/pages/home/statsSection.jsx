const StatsSection = () => {

    const stats = [

        {
            number: "10K+",
            title: "Generated Plans"
        },

        {
            number: "5K+",
            title: "Happy Users"
        },

        {
            number: "1K+",
            title: "Premium Members"
        },

        {
            number: "24/7",
            title: "AI Support"
        }

    ];

    return (

        <section className="stats-section fade-in">

            <div className="stats-container">

                {
                    stats.map((item, index) => (

                        <div
                            className="stats-card"
                            key={index}
                        >

                            <h2>{item.number}</h2>

                            <p>{item.title}</p>

                        </div>

                    ))
                }

            </div>

        </section>

    );

};

export default StatsSection;