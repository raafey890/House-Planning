import EditProfile from "./EditProfile.jsx";
import SavedProjects from "./SavedProjects.jsx";
import BillingHistory from "./BillingHistory.jsx";

function ProfilePage() {

    return (

        <div className="profile-page">

            <h1>
                User Profile
            </h1>

            <EditProfile />

            <SavedProjects />

            <BillingHistory />

        </div>

    );

}

export default ProfilePage;