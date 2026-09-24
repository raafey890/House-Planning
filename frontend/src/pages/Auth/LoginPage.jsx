import { useState } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import { useAuthStore } from "../../store";
import { Box } from "lucide-react";
import "../../styles/pages/auth.css";

function LoginPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    
    const signIn = useAuthStore((state) => state.signIn);
    const loading = useAuthStore((state) => state.loading);
    const error = useAuthStore((state) => state.error);
    const clearError = useAuthStore((state) => state.clearError);
    const navigate = useNavigate();
    const location = useLocation();

    async function handleLogin(event) {
        event.preventDefault();
        clearError();
        const { error } = await signIn(email, password);
        if (!error) {
            const returnTo = location.state?.returnTo || "/dashboard";
            navigate(returnTo, { replace: true });
        }
    }

    return (
        <div className="auth-page">
            <div className="auth-split-visual">
                <div className="auth-brand-statement">
                    <h2>Welcome back.</h2>
                    <p>Continue shaping your architectural vision with our AI-powered planning tools.</p>
                </div>
            </div>
            
            <div className="auth-content">
                <div className="auth-card">
                    <div className="auth-header">
                        <Link to="/" className="auth-logo"><Box size={28} color="var(--color-primary)" /> AI House Planner</Link>
                        <h1>Sign In</h1>
                        <p>Enter your credentials to access your workspace</p>
                    </div>

                    {error && <div className="error-message">{error}</div>}
                    
                    <form onSubmit={handleLogin} className="auth-form">
                        <div className="form-group">
                            <label className="form-label">Email Address</label>
                            <input
                                className="form-control"
                                type="email"
                                placeholder="name@company.com"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Password</label>
                            <input
                                className="form-control"
                                type="password"
                                placeholder="••••••••"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>
                        
                        <button type="submit" className="btn btn-primary btn-lg" style={{ width: '100%', marginTop: 'var(--space-2)' }} disabled={loading}>
                            {loading ? "Signing in..." : "Sign In"}
                        </button>
                    </form>
                    
                    <p className="auth-link">
                        Don't have an account? <Link to="/signup">Create one</Link>
                    </p>
                </div>
            </div>
        </div>
    );
}

export default LoginPage;