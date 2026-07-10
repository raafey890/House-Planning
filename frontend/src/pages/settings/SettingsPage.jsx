import ThemeSettings from "./ThemeSettings.jsx";
import NotificationSettings from "./NotificationSettings.jsx";
import SecuritySettings from "./SecuritySettings.jsx";

function SettingsPage() {

    return (

        <div className="settings-page">

            <h1>
                Settings
            </h1>

            <ThemeSettings />

            <NotificationSettings />

            <SecuritySettings />

        </div>

    );

}

export default SettingsPage;