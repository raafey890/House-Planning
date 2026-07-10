import ExteriorGallery from "./ExteriorGallery.jsx";
import InteriorGallery from "./InteriorGallery.jsx";
import FilterPanel from "./FilterPanel.jsx";

function GalleryPage() {

    return (

        <div className="gallery-page">

            <h1>
                Design Gallery
            </h1>

            <FilterPanel />

            <ExteriorGallery />

            <InteriorGallery />

        </div>

    );

}

export default GalleryPage;