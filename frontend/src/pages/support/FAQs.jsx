const faqs = [

    {
        id: 1,
        question:
        "How to generate AI house designs?",

        answer:
        "Go to AI Studio and enter prompt."
    },

    {
        id: 2,
        question:
        "How to download floor plans?",

        answer:
        "Open FloorPlan section and export."
    },

    {
        id: 3,
        question:
        "How to upgrade premium?",

        answer:
        "Visit Premium page and select plan."
    }

];

function FAQs() {

    return (

        <div className="faq-section">

            <h2>
                Frequently Asked Questions
            </h2>

            {

                faqs.map(item => (

                    <div
                        key={item.id}
                        className="faq-card"
                    >

                        <h3>
                            {item.question}
                        </h3>

                        <p>
                            {item.answer}
                        </p>

                    </div>

                ))

            }

        </div>

    );

}

export default FAQs;