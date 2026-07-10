import SubscriptionPlans from "./SubscriptionPlans.jsx";
import UpgradeBenefits from "./UpgradeBenefits.jsx";
import PaymentPage from "./PaymentPage.jsx";

function PremiumPage() {

    return (

        <div className="premium-page">

            <h1>
                Premium Membership
            </h1>

            <SubscriptionPlans />

            <UpgradeBenefits />

            <PaymentPage />

        </div>

    );

}

export default PremiumPage;