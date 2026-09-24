import EditProfile from "./EditProfile.jsx";

function ProfilePage() {
    return (
        <div style={{ maxWidth: 'var(--container-max-width)', margin: '0 auto' }}>
            <div style={{ marginBottom: 'var(--space-8)' }}>
                <h1 className="text-h2" style={{ margin: 0 }}>Account Settings</h1>
                <p className="text-muted" style={{ margin: 0 }}>Manage your personal information and preferences.</p>
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 'var(--space-6)', maxWidth: '600px' }}>
                <EditProfile />
            </div>
        </div>
    );
}

export default ProfilePage;