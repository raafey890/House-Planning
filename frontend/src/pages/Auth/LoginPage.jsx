import { useState } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import { useAuthStore } from "../../store";
import { Box, Eye, EyeOff, Loader2 } from "lucide-react";
import "../../styles/pages/auth.css";

function LoginPage() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [showPassword, setShowPassword] = useState(false);
    
    // Resend confirmation state
    const [resendStatus, setResendStatus] = useState({ loading: false, message: "", error: "" });

    const signIn = useAuthStore((state) => state.signIn);
    const resendConfirmation = useAuthStore((state) => state.resendConfirmation);
    const loading = useAuthStore((state) => state.loading);
    const error = useAuthStore((state) => state.error);
    const clearError = useAuthStore((state) => state.clearError);
    const navigate = useNavigate();
    const location = useLocation();

    async function handleLogin(event) {
        event.preventDefault();
        clearError();
        setResendStatus({ loading: false, message: "", error: "" });
        const { error } = await signIn(email, password);
        if (!error) {
            const returnTo = location.state?.returnTo || "/dashboard";
            navigate(returnTo, { replace: true });
        }
    }

    async function handleResendEmail() {
        setResendStatus({ loading: true, message: "", error: "" });
        const { error } = await resendConfirmation(email);
        if (error) {
            setResendStatus({ loading: false, message: "", error: error.message });
        } else {
            setResendStatus({ loading: false, message: "Confirmation email sent. Please check your inbox.", error: "" });
        }
    }

    const isUnconfirmed = error && error.toLowerCase().includes("email not confirmed");

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

                    {error && (
                        <div className="error-message">
                            {isUnconfirmed ? (
                                <div>
                                    <p style={{ margin: 0 }}>
                                        Your email address has not been verified yet. Please check your inbox and confirm your email before signing in.
                                    </p>
                                    <div style={{ marginTop: '10px' }}>
                                        <button
                                            type="button"
                                            onClick={handleResendEmail}
                                            disabled={resendStatus.loading}
                                            style={{
                                                background: 'none',
                                                border: 'none',
                                                color: 'var(--color-accent)',
                                                fontWeight: 600,
                                                cursor: 'pointer',
                                                padding: 0,
                                                fontSize: '0.875rem',
                                                textDecoration: 'underline'
                                            }}
                                        >
                                            {resendStatus.loading ? "Sending..." : "Resend confirmation email"}
                                        </button>
                                    </div>
                                </div>
                            ) : (
                                error
                            )}
                        </div>
                    )}

                    {resendStatus.message && (
                        <div className="success-message" style={{ backgroundColor: '#ecfdf5', color: 'var(--color-success)', padding: 'var(--space-3)', borderRadius: 'var(--radius-md)', marginBottom: 'var(--space-4)', borderLeft: '4px solid var(--color-success)' }}>
                            {resendStatus.message}
                        </div>
                    )}

                    {resendStatus.error && (
                        <div className="error-message" style={{ marginTop: 'var(--space-2)' }}>
                            {resendStatus.error}
                        </div>
                    )}
                    
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
                            <div className="password-input-wrapper">
                                <input
                                    className="form-control"
                                    type={showPassword ? "text" : "password"}
                                    placeholder="••••••••"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                />
                                <button
                                    type="button"
                                    className="password-toggle-btn"
                                    onClick={() => setShowPassword(!showPassword)}
                                    aria-label={showPassword ? "Hide password" : "Show password"}
                                >
                                    {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                                </button>
                            </div>
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