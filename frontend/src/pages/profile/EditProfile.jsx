import { useState, useEffect } from "react";
import { useAuthStore } from "../../store";
import { supabase } from "../../lib/supabase";
import toast from "react-hot-toast";
import { User, Camera, Mail, Phone, MapPin } from "lucide-react";

function EditProfile() {
    const { profile, session, updateProfile } = useAuthStore();
    
    const [name, setName] = useState("");
    const [phone, setPhone] = useState("");
    const [address, setAddress] = useState("");
    const [avatarUrl, setAvatarUrl] = useState("");
    
    const [loading, setLoading] = useState(false);
    const [uploading, setUploading] = useState(false);

    useEffect(() => {
        if (profile) {
            setName(profile.full_name || "");
            setPhone(profile.phone || "");
            setAddress(profile.address || "");
            setAvatarUrl(profile.avatar_url || "");
        }
    }, [profile]);

    async function handleAvatarUpload(event) {
        try {
            setUploading(true);
            
            if (!event.target.files || event.target.files.length === 0) {
                throw new Error('You must select an image to upload.');
            }
            
            const file = event.target.files[0];
            const fileExt = file.name.split('.').pop();
            const fileName = `${session.user.id}-${Math.random()}.${fileExt}`;
            const filePath = `${session.user.id}/${fileName}`;

            const toastId = toast.loading("Uploading avatar...");

            const { error: uploadError } = await supabase.storage
                .from('avatars')
                .upload(filePath, file);

            if (uploadError) throw uploadError;

            const { data } = supabase.storage.from('avatars').getPublicUrl(filePath);
            
            await updateProfile({ avatar_url: data.publicUrl });
            setAvatarUrl(data.publicUrl);
            toast.success("Avatar updated successfully!", { id: toastId });
        } catch (error) {
            toast.error(error.message);
        } finally {
            setUploading(false);
        }
    }

    async function saveProfile(event) {
        event.preventDefault();
        setLoading(true);
        const toastId = toast.loading("Saving profile...");

        const { error } = await updateProfile({
            full_name: name,
            phone: phone,
            address: address
        });

        if (error) {
            toast.error(`Error: ${error.message}`, { id: toastId });
        } else {
            toast.success("Profile updated successfully!", { id: toastId });
        }
        setLoading(false);
    }

    return (
        <div className="card card-body">
            <h3 className="text-h4 mb-6" style={{ borderBottom: '1px solid var(--color-border)', paddingBottom: 'var(--space-4)' }}>Personal Information</h3>
            
            <div style={{ marginBottom: 'var(--space-8)', display: 'flex', alignItems: 'center', gap: 'var(--space-6)' }}>
                <div style={{ position: 'relative' }}>
                    {avatarUrl ? (
                        <img src={avatarUrl} alt="Avatar" style={{ width: '80px', height: '80px', borderRadius: '50%', objectFit: 'cover' }} />
                    ) : (
                        <div style={{ width: '80px', height: '80px', borderRadius: '50%', backgroundColor: 'var(--color-surface-alt)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <User size={32} color="var(--color-text-muted)" />
                        </div>
                    )}
                    
                    <label style={{ 
                        position: 'absolute', bottom: '-4px', right: '-4px', 
                        width: '32px', height: '32px', borderRadius: '50%', 
                        backgroundColor: 'var(--color-primary)', color: 'white', 
                        display: 'flex', alignItems: 'center', justifyContent: 'center', 
                        cursor: 'pointer', border: '2px solid var(--color-surface-card)',
                        boxShadow: 'var(--shadow-sm)'
                    }}>
                        <Camera size={16} />
                        <input type="file" accept="image/*" onChange={handleAvatarUpload} disabled={uploading} style={{ display: 'none' }} />
                    </label>
                </div>
                
                <div>
                    <div style={{ fontWeight: 600, fontSize: '1.1rem' }}>{name || "Set your name"}</div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--color-text-muted)' }}>{session?.user?.email}</div>
                </div>
            </div>

            <form onSubmit={saveProfile} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
                <div className="form-group">
                    <label className="form-label"><User size={14} style={{ display: 'inline', marginRight: '4px' }}/> Full Name</label>
                    <input className="form-control" type="text" value={name} onChange={(e) => setName(e.target.value)} required />
                </div>

                <div className="form-group">
                    <label className="form-label"><Mail size={14} style={{ display: 'inline', marginRight: '4px' }}/> Email Address</label>
                    <input className="form-control" type="email" value={session?.user?.email || ""} readOnly disabled style={{ backgroundColor: 'var(--color-surface-alt)', cursor: 'not-allowed' }} />
                    <small className="text-muted">Email cannot be changed directly.</small>
                </div>

                <div className="form-group">
                    <label className="form-label"><Phone size={14} style={{ display: 'inline', marginRight: '4px' }}/> Phone Number</label>
                    <input className="form-control" type="text" placeholder="+1 (555) 000-0000" value={phone} onChange={(e) => setPhone(e.target.value)} />
                </div>
                
                <div className="form-group">
                    <label className="form-label"><MapPin size={14} style={{ display: 'inline', marginRight: '4px' }}/> Address</label>
                    <input className="form-control" type="text" placeholder="City, Country" value={address} onChange={(e) => setAddress(e.target.value)} />
                </div>

                <button type="submit" className="btn btn-primary mt-4" disabled={loading}>
                    {loading ? "Saving Changes..." : "Save Profile"}
                </button>
            </form>
        </div>
    );
}

export default EditProfile;