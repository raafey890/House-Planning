import FAQs from "./FAQs.jsx";
import ContactSupport from "./ContactSupport.jsx";
import ReportIssue from "./ReportIssue.jsx";

function SupportPage() {

    return (

        <div className="support-page">

            <h1>
                Support Center
            </h1>

            <FAQs />

            <ContactSupport />

            <ReportIssue />

        </div>

    );

}

export default SupportPage;