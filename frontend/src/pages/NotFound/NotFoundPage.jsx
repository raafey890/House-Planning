import { Link } from "react-router-dom";

function NotFoundPage() {

    return (

        <div className="notfound-page">

            <div className="notfound-container">

                <h1>
                    404
                </h1>

                <h2>
                    Page Not Found
                </h2>

                <p>
                    The page you are looking for
                    does not exist.
                </p>

                <Link to="/">

                    <button>
                        Go To Home
                    </button>

                </Link>

            </div>

        </div>

    );

}

export default NotFoundPage;