function useNotifications() {

    const showNotification = (message) => {

        console.log(message);

    };

    return {

        showNotification

    };
}

export default useNotifications;