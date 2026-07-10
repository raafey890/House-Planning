const invoiceGenerator = {

    generateInvoice(orderData) {

        const invoice = {

            invoiceId:
            `INV-${Date.now()}`,

            customer: orderData.customer,

            amount: orderData.amount,

            createdAt: new Date()

        };

        console.log("Invoice Generated");

        return invoice;

    },

    downloadInvoice(invoiceId) {

        console.log(
            `Downloading Invoice ${invoiceId}`
        );

    }

};

export default invoiceGenerator;