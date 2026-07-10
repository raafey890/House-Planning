import { Navigate } from "react-router-dom";

function ProtectedRoute({ children }) {

    const isAuthenticated = true;

    return isAuthenticated
        ? children
        : <Navigate to="/login" />;

}

export default ProtectedRoute;