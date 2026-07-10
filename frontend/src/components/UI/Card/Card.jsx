import "./Card.css";

function Card({ title, description, children }) {

    return (

        <div className="custom-card">

            {title && <h3>{title}</h3>}

            {description && <p>{description}</p>}

            {children}

        </div>

    );

}

export default Card;