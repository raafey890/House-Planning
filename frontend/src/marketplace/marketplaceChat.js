const marketplaceChat = {

    conversations: [],

    createConversation(
        userId,
        providerId
    ) {

        const conversation = {

            id: Date.now(),

            userId,

            providerId,

            messages: []

        };

        this.conversations.push(
            conversation
        );

        return conversation;

    },

    sendMessage(
        conversationId,
        sender,
        message
    ) {

        const conversation =
        this.conversations.find(
            item => item.id === conversationId
        );

        if(conversation) {

            conversation.messages.push({

                sender,

                message,

                sentAt: new Date()

            });

        }

    },

    getConversation(conversationId) {

        return this.conversations.find(
            item => item.id === conversationId
        );

    }

};

export default marketplaceChat;