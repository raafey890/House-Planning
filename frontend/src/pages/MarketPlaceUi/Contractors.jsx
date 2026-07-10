const contractors = [

    {
        id: 1,
        name: "Rahul Constructions",
        experience: "8 Years",
        rating: 4.8
    },

    {
        id: 2,
        name: "Modern Builders",
        experience: "5 Years",
        rating: 4.5
    }

];

function Contractors() {

    return (

        <div className="contractors-section">

            <h2>
                Contractors
            </h2>

            <div className="contractor-grid">

                {

                    contractors.map(item => (

                        <div
                            key={item.id}
                            className="contractor-card"
                        >

                            <h3>
                                {item.name}
                            </h3>

                            <p>
                                Experience:
                                {item.experience}
                            </p>

                            <p>
                                Rating:
                                {item.rating}
                            </p>

                            <button>
                                Hire Now
                            </button>

                        </div>

                    ))

                }

            </div>

        </div>

    );

}

export default Contractors;