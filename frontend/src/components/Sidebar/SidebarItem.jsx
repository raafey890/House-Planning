import { Link } from "react-router-dom";

function SidebarItem({
    title,
    path
}) {

    return (

        <Link
            to={path}
            className="sidebar-item"
        >

            {title}

        </Link>

    );

}

export default SidebarItem;