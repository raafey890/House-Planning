const emailNotifications = {

    sentEmails: [],

    templates: {

        welcome:
        "Welcome to AI House Planner",

        premium:
        "Upgrade to Premium Today",

        designReady:
        "Your AI Design is Ready"

    },

    sendEmail(email, subject, content) {

        const mail = {

            email,

            subject,

            content,

            sentAt: new Date()

        };

        this.sentEmails.push(mail);

        console.log(
            `Email Sent To ${email}`
        );

    },

    sendTemplateEmail(email, templateName) {

        const template =
        this.templates[templateName];

        this.sendEmail(
            email,
            templateName,
            template
        );

    }

};

export default emailNotifications;