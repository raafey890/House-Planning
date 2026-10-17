const fs = require('fs');
let code = fs.readFileSync('src/pages/Projects/ProjectWorkspace.jsx', 'utf8');

// Replace the specific block
code = code.replace(/{project\.plot_length && project\.plot_width \? \([\s\S]*?\) : \(/, 
\{project.plot_width && project.plot_length ? (
                                <>
                                    <span style={{ fontWeight: 600, color: 'var(--color-primary)' }}>{project.plot_width} × {project.plot_length} ft</span>
                                    <span style={{ opacity: 0.4 }}>•</span>
                                    <span>{project.facing || 'Not set'} Facing</span>
                                    <span style={{ opacity: 0.4 }}>•</span>
                                    <span>G + {(project.floors || 1) - 1}</span>
                                    <span style={{ opacity: 0.4 }}>•</span>
                                    <span>{project.design_style || 'Style not set'}</span>
                                </>
                            ) : (\
);

fs.writeFileSync('src/pages/Projects/ProjectWorkspace.jsx', code, 'utf8');
