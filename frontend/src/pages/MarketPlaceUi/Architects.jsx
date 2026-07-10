const architects = [

    {
        id: 1,
        name: "Ayaan Architects",
        specialty: "Luxury Villas",
        rating: 4.9
    },

    {
        id: 2,
        name: "Urban Design Studio",
        specialty: "Modern Homes",
        rating: 4.7
    }

];

function Architects() {

    return (

        <div className="architects-section">

            <h2>
                Architects
            </h2>

            <div className="architect-grid">

                {

                    architects.map(item => (

                        <div
                            key={item.id}
                            className="architect-card"
                        >

                            <h3>
                                {item.name}
                            </h3>

                            <p>
                                Specialty:
                                {item.specialty}
                            </p>

                            <p>
                                Rating:
                                {item.rating}
                            </p>

                            <button>
                                View Portfolio
                            </button>

                        </div>

                    ))

                }

            </div>

        </div>

    );

}

export default Architects;