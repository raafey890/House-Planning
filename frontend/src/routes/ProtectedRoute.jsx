import { Navigate, useLocation } from "react-router-dom";
import { useAuthStore } from "../store";

function ProtectedRoute({ children }) {
  const { session, initialized } = useAuthStore();
  const location = useLocation();

  if (!initialized) {
    return (
      <div className="flex justify-center items-center h-screen w-full bg-slate-50">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
        <p className="ml-4 text-slate-600">Loading...</p>
      </div>
    );
  }

  if (!session) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}

export default ProtectedRoute;