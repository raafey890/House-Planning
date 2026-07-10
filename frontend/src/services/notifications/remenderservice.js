function reminderService(task) {

    console.log("Reminder Created");

    console.log(task);

    return {

        status: "success",

        reminder: task

    };
}

export default reminderService;