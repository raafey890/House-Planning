import { useState } from "react";

function ThemeSettings() {

    const [theme, setTheme] =
    useState("Light");

    return (

        <div className="theme-settings">

            <h2>
                Theme Settings
            </h2>

            <select
                value={theme}
                onChange={(event) =>
                    setTheme(
                        event.target.value
                    )
                }
            >

                <option>
                    Light
                </option>

                <option>
                    Dark
                </option>

                <option>
                    System
                </option>

            </select>

            <p>
                Selected Theme:
                {theme}
            </p>

        </div>

    );

}

export default ThemeSettings;