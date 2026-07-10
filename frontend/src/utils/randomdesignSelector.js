function randomDesignSelector(designs) {

    const randomIndex = Math.floor(
        Math.random() * designs.length
    );

    return designs[randomIndex];
}

export default randomDesignSelector;