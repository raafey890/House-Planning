const serviceBookings = {

    bookings: [],

    createBooking(serviceData) {

        const booking = {

            id: Date.now(),

            ...serviceData,

            status: "pending",

            createdAt: new Date()

        };

        this.bookings.push(booking);

        return booking;

    },

    updateBookingStatus(
        bookingId,
        status
    ) {

        const booking =
        this.bookings.find(
            item => item.id === bookingId
        );

        if(booking) {

            booking.status = status;

        }

    },

    getUserBookings(userId) {

        return this.bookings.filter(
            booking =>
            booking.userId === userId
        );

    }

};

export default serviceBookings;