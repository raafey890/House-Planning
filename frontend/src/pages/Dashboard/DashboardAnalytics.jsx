import React from "react";
import { useProjectStore } from "../../store";
import { FolderKanban, Map, Calculator, PenTool } from "lucide-react";

const DashboardAnalytics = () => {
    const { projects } = useProjectStore();

    // Derived real metrics
    const totalProjects = projects.length;
    const draftedPlots = projects.filter(p => p.plot_length && p.plot_width).length;

    const analyticsData = [
        {
            title: "Total Workspaces",
            value: totalProjects,
            icon: <FolderKanban size={24} color="var(--color-primary)" />,
            subtitle: "Active projects"
        },
        {
            title: "Defined Plots",
            value: draftedPlots,
            icon: <Map size={24} color="var(--color-accent)" />,
            subtitle: "Configured requirements"
        },
        {
            title: "AI Floor Plans",
            value: 0,
            icon: <PenTool size={24} color="var(--color-text-muted)" />,
            subtitle: "Coming in next phase"
        },
        {
            title: "Cost Estimates",
            value: 0, 
            icon: <Calculator size={24} color="var(--color-text-muted)" />,
            subtitle: "Coming in next phase"
        }
    ];

    return (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 'var(--space-6)' }}>
            {analyticsData.map((item, index) => (
                <div key={index} className="card card-body" style={{ display: 'flex', flexDirection: 'column' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 'var(--space-4)' }}>
                        <h3 className="text-muted" style={{ margin: 0, fontSize: '0.95rem', fontWeight: 600 }}>{item.title}</h3>
                        <div style={{ padding: '8px', background: 'var(--color-surface-alt)', borderRadius: '8px' }}>
                            {item.icon}
                        </div>
                    </div>
                    <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--color-primary)', marginBottom: '4px' }}>
                        {item.value}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                        {item.subtitle}
                    </div>
                </div>
            ))}
        </div>
    );
};

export default DashboardAnalytics;