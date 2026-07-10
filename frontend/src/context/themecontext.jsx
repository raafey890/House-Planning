const ThemeContext = {

    currentTheme: "light",

    availableThemes: [

        "light",
        "dark",
        "luxury"

    ],

    animationsEnabled: true,

    changeTheme(themeName) {

        if(this.availableThemes.includes(themeName)) {

            this.currentTheme = themeName;

            console.log(`Theme changed to ${themeName}`);

        }

    },

    toggleAnimations() {

        this.animationsEnabled =
        !this.animationsEnabled;

        console.log(
            `Animations: ${this.animationsEnabled}`
        );

    },

    resetTheme() {

        this.currentTheme = "light";

    }

};

export default ThemeContext;