const pageTransitions = {

    currentPage: "home",

    transitionDuration: 500,

    navigateTo(pageName) {

        console.log(
            `Transitioning To ${pageName}`
        );

        this.currentPage = pageName;

    },

    fadeTransition() {

        console.log("Fade Transition Applied");

    },

    slideTransition() {

        console.log("Slide Transition Applied");

    }

};

export default pageTransitions;