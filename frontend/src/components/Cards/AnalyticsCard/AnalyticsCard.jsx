import "./AnalyticsCard.css";

function AnalyticsCard({
    title,
    value,
    growth
}) {

    return (

        <div className="analytics-card">

            <h4>
                {title}
            </h4>

            <h1>
                {value}
            </h1>

            <p>
                {growth}
            </p>

        </div>

    );

}

export default AnalyticsCard;