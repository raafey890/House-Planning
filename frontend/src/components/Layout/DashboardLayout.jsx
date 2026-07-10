function DashboardLayout({ children }) {

    return (

        <div className="dashboard-layout">

            <aside className="dashboard-sidebar">

                <h2>
                    Dashboard
                </h2>

                <ul>

                    <li>
                        Overview
                    </li>

                    <li>
                        Projects
                    </li>

                    <li>
                        Analytics
                    </li>

                    <li>
                        Settings
                    </li>

                </ul>

            </aside>

            <section className="dashboard-content">

                {children}

            </section>

        </div>

    );

}

export default DashboardLayout;