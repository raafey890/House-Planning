import { useState } from "react";

function EditProfile() {

    const [name, setName] =
    useState("Raafey");

    const [email, setEmail] =
    useState("raafey@gmail.com");

    const [phone, setPhone] =
    useState("");

    function saveProfile(event) {

        event.preventDefault();

        console.log(
            "Profile Updated"
        );

    }

    return (

        <div className="edit-profile">

            <h2>
                Edit Profile
            </h2>

            <form onSubmit={saveProfile}>

                <input
                    type="text"
                    value={name}
                    onChange={(event) =>
                        setName(
                            event.target.value
                        )
                    }
                />

                <input
                    type="email"
                    value={email}
                    onChange={(event) =>
                        setEmail(
                            event.target.value
                        )
                    }
                />

                <input
                    type="text"
                    placeholder="Phone Number"
                    value={phone}
                    onChange={(event) =>
                        setPhone(
                            event.target.value
                        )
                    }
                />

                <button type="submit">

                    Save Changes

                </button>

            </form>

        </div>

    );

}

export default EditProfile;