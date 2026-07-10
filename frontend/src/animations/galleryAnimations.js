const galleryAnimations = {

    fadeInGallery() {

        console.log("Gallery Fade In Animation");

    },

    zoomImage(imageId) {

        console.log(`Zoom Animation For ${imageId}`);

    },

    slideGallery(direction) {

        console.log(`Sliding Gallery ${direction}`);

    },

    showImagePreview(imageId) {

        console.log(`Preview Opened For ${imageId}`);

    },

    closeImagePreview() {

        console.log("Preview Closed");

    }

};

export default galleryAnimations;