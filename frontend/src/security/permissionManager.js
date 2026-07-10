const permissionManager = {

    roles: {

        admin: [

            "manage_users",
            "manage_projects",
            "view_analytics"

        ],

        premiumUser: [

            "generate_hd_designs",
            "save_unlimited_projects"

        ],

        guest: [

            "view_gallery"

        ]

    },

    hasPermission(role, permission) {

        return this.roles[role]?.includes(
            permission
        );

    }

};

export default permissionManager;