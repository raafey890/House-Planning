import { useState } from "react";
import { useNavigate, useLocation, Link } from "react-router-dom";
import { useAuthStore } from "../../store";
import { Box } from "lucide-react";
import "../../styles/pages/auth.css";

function SignupPage() {
    const [fullName, setFullName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [successMsg, setSuccessMsg] = useState("");
    
    const signUp = useAuthStore((state) => state.signUp);
    const loading = useAuthStore((state) => state.loading);
    const error = useAuthStore((state) => state.error);
    const clearError = useAuthStore((state) => state.clearError);
    const navigate = useNavigate();
    const location = useLocation();

    async function handleSignup(event) {
        event.preventDefault();
        clearError();
        setSuccessMsg("");
        
        const { error } = await signUp(email, password, fullName);
        if (!error) {
            const returnTo = location.state?.returnTo || "/dashboard";
            setSuccessMsg("Account created successfully! Redirecting...");
            setTimeout(() => navigate(returnTo, { replace: true }), 1500);
        }
    }

    return (
        <div className="auth-page">
            <div className="auth-split-visual" style={{ background: 'url("https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&q=80&w=1200") center/cover' }}>
                <div className="auth-brand-statement">
                    <h2>Start your journey.</h2>
                    <p>Create your first intelligent house project today.</p>
                </div>
            </div>
            
            <div className="auth-content">
                <div className="auth-card">
                    <div className="auth-header">
                        <Link to="/" className="auth-logo"><Box size={28} color="var(--color-primary)" /> AI House Planner</Link>
                        <h1>Create Account</h1>
                        <p>Join the next generation of architectural planning</p>
                    </div>

                    {error && <div className="error-message">{error}</div>}
                    {successMsg && <div className="success-message" style={{ backgroundColor: '#ecfdf5', color: 'var(--color-success)', padding: 'var(--space-3)', borderRadius: 'var(--radius-md)', marginBottom: 'var(--space-4)', borderLeft: '4px solid var(--color-success)' }}>{successMsg}</div>}
                    
                    <form onSubmit={handleSignup} className="auth-form">
                        <div className="form-group">
                            <label className="form-label">Full Name</label>
                            <input
                                className="form-control"
                                type="text"
                                placeholder="John Doe"
                                value={fullName}
                                onChange={(e) => setFullName(e.target.value)}
                                required
                            />
                        </div>
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
                                placeholder="•••••••• (min 6 chars)"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                                minLength={6}
                            />
                        </div>
                        
                        <button type="submit" className="btn btn-primary btn-lg" style={{ width: '100%', marginTop: 'var(--space-2)' }} disabled={loading}>
                            {loading ? "Creating account..." : "Sign Up"}
                        </button>
                    </form>
                    
                    <p className="auth-link">
                        Already have an account? <Link to="/login">Sign in</Link>
                    </p>
                </div>
            </div>
        </div>
    );
}

export default SignupPage;