import { Link, useNavigate } from "react-router-dom";
import { useAuthStore } from "../../store";
import { User, LogOut } from 'lucide-react';

function UserMenu() {
    const { session, signOut, profile } = useAuthStore();
    const navigate = useNavigate();

    const handleLogout = async () => {
        await signOut();
        navigate("/");
    };

    return (
        <div className="user-menu" style={{ display: 'flex', gap: 'var(--space-3)', alignItems: 'center' }}>
            {session ? (
                <>
                    <Link to="/dashboard" className="btn btn-ghost" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        {profile?.avatar_url ? (
                            <img src={profile.avatar_url} alt="Avatar" style={{ width: '28px', height: '28px', borderRadius: '50%', objectFit: 'cover' }} />
                        ) : (
                            <User size={18} />
                        )}
                        <span>{profile?.full_name?.split(' ')[0] || "Dashboard"}</span>
                    </Link>
                    <button onClick={handleLogout} className="btn btn-outline btn-sm" title="Logout">
                        <LogOut size={16} />
                    </button>
                </>
            ) : (
                <>
                    <Link to="/login" className="btn btn-ghost btn-sm">Login</Link>
                    <Link to="/signup" className="btn btn-primary btn-sm">Get Started</Link>
                </>
            )}
        </div>
    );
}

export default UserMenu;