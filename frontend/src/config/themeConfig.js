const themeConfig = {

    themes: {

        light: {

            background: "#ffffff",

            text: "#000000"

        },

        dark: {

            background: "#121212",

            text: "#ffffff"

        },

        luxury: {

            background: "#1e1e1e",

            text: "#d4af37"

        }

    },

    currentTheme: "light",

    setTheme(themeName) {

        if(this.themes[themeName]) {

            this.currentTheme = themeName;

        }

    },

    getTheme() {

        return this.themes[this.currentTheme];

    }

};

export default themeConfig;