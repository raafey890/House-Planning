import { useState } from "react";

function ContactSupport() {

    const [name, setName] =
    useState("");

    const [message, setMessage] =
    useState("");

    function sendMessage(event) {

        event.preventDefault();

        console.log(
            "Support Message Sent"
        );

    }

    return (

        <div className="contact-support">

            <h2>
                Contact Support
            </h2>

            <form onSubmit={sendMessage}>

                <input
                    type="text"
                    placeholder="Your Name"
                    value={name}
                    onChange={(event) =>
                        setName(
                            event.target.value
                        )
                    }
                />

                <textarea
                    placeholder="Describe your issue"
                    value={message}
                    onChange={(event) =>
                        setMessage(
                            event.target.value
                        )
                    }
                />

                <button type="submit">

                    Send Message

                </button>

            </form>

        </div>

    );

}

export default ContactSupport;