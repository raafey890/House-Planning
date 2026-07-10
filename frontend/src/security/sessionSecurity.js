const sessionSecurity = {

    sessionTimeout: 3600000,

    activeSessions: [],

    createSession(userId) {

        const session = {

            userId,

            createdAt: Date.now()

        };

        this.activeSessions.push(session);

        return session;

    },

    destroySession(userId) {

        this.activeSessions =
        this.activeSessions.filter(
            session => session.userId !== userId
        );

    },

    isSessionExpired(session) {

        return (
            Date.now() - session.createdAt
        ) > this.sessionTimeout;

    }

};

export default sessionSecurity;