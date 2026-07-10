const interiorImages = [

    {
        id: 1,
        image:
        "/assets/images/interior/living1.jpg",
        title: "Luxury Living Room"
    },

    {
        id: 2,
        image:
        "/assets/images/interior/bedroom1.jpg",
        title: "Modern Bedroom"
    }

];

function InteriorGallery() {

    return (

        <section className="interior-gallery">

            <h2>
                Interior Designs
            </h2>

            <div className="gallery-grid">

                {

                    interiorImages.map(item => (

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

export default InteriorGallery;