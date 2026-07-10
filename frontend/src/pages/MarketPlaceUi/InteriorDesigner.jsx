const designers = [

    {
        id: 1,
        name: "Elegant Interiors",
        style: "Modern Interior",
        rating: 4.8
    },

    {
        id: 2,
        name: "Luxury Decor Studio",
        style: "Luxury Interior",
        rating: 4.6
    }

];

function InteriorDesigners() {

    return (

        <div className="interior-designers">

            <h2>
                Interior Designers
            </h2>

            <div className="designer-grid">

                {

                    designers.map(item => (

                        <div
                            key={item.id}
                            className="designer-card"
                        >

                            <h3>
                                {item.name}
                            </h3>

                            <p>
                                Style:
                                {item.style}
                            </p>

                            <p>
                                Rating:
                                {item.rating}
                            </p>

                            <button>
                                Contact Designer
                            </button>

                        </div>

                    ))

                }

            </div>

        </div>

    );

}

export default InteriorDesigners;