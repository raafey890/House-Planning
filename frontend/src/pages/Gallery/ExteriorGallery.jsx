const exteriorImages = [

    {
        id: 1,
        image:
        "/assets/images/exterior/modern1.jpg",
        title: "Modern Villa"
    },

    {
        id: 2,
        image:
        "/assets/images/exterior/luxury1.jpg",
        title: "Luxury Duplex"
    }

];

function ExteriorGallery() {

    return (

        <section className="exterior-gallery">

            <h2>
                Exterior Designs
            </h2>

            <div className="gallery-grid">

                {

                    exteriorImages.map(item => (

                        <div
                            key={item.id}
                            className="gallery-card"
                        >

                            <img
                                src={item.image}
                                alt={item.title}
                            />

                            <h3>
                                {item.title}
                            </h3>

                        </div>

                    ))

                }

            </div>

        </section>

    );

}

export default ExteriorGallery;