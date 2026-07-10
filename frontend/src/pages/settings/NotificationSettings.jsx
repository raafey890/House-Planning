import { useState } from "react";

function NotificationSettings() {

    const [emailNotification,
    setEmailNotification] =
    useState(true);

    const [pushNotification,
    setPushNotification] =
    useState(true);

    return (

        <div className="notification-settings">

            <h2>
                Notification Settings
            </h2>

            <label>

                <input
                    type="checkbox"
                    checked={emailNotification}
                    onChange={() =>
                        setEmailNotification(
                            !emailNotification
                        )
                    }
                />

                Email Notifications

            </label>

            <label>

                <input
                    type="checkbox"
                    checked={pushNotification}
                    onChange={() =>
                        setPushNotification(
                            !pushNotification
                        )
                    }
                />

                Push Notifications

            </label>

        </div>

    );

}

export default NotificationSettings;