import React from "react";
import { useProjectStore } from "../../store";
import { Clock } from "lucide-react";

const RecentActivities = () => {
    const { projects } = useProjectStore();

    // Generate real activity from projects
    const activities = projects
        .map(p => ({
            id: p.id,
            action: `Created workspace "${p.name}"`,
            date: new Date(p.created_at)
        }))
        .sort((a, b) => b.date - a.date)
        .slice(0, 5);

    if (activities.length === 0) return null;

    return (
        <div className="card card-body">
            <h3 className="text-h3" style={{ margin: '0 0 var(--space-6) 0' }}>Activity Log</h3>
            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
                {activities.map((activity, index) => (
                    <li key={index} style={{ display: 'flex', alignItems: 'flex-start', gap: 'var(--space-3)' }}>
                        <Clock size={16} color="var(--color-accent)" style={{ marginTop: '2px' }} />
                        <div>
                            <div style={{ fontWeight: 500, color: 'var(--color-primary)', fontSize: '0.95rem' }}>{activity.action}</div>
                            <div style={{ fontSize: '0.8rem', color: 'var(--color-text-muted)', marginTop: '2px' }}>{activity.date.toLocaleDateString()} at {activity.date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
                        </div>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default RecentActivities;