function imageStorageService(images) {

    console.log("Saving Generated Images");

    console.log(images);

    return {

        status: "success",

        savedImages: images

    };
}

export default imageStorageService;