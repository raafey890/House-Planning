import { useState } from "react";

function ReportIssue() {

    const [issue, setIssue] =
    useState("");

    const [priority, setPriority] =
    useState("Medium");

    function submitIssue(event) {

        event.preventDefault();

        console.log(
            "Issue Report Submitted"
        );

    }

    return (

        <div className="report-issue">

            <h2>
                Report Issue
            </h2>

            <form onSubmit={submitIssue}>

                <textarea
                    placeholder="Describe issue"
                    value={issue}
                    onChange={(event) =>
                        setIssue(
                            event.target.value
                        )
                    }
                />

                <select
                    value={priority}
                    onChange={(event) =>
                        setPriority(
                            event.target.value
                        )
                    }
                >

                    <option>
                        Low
                    </option>

                    <option>
                        Medium
                    </option>

                    <option>
                        High
                    </option>

                </select>

                <button type="submit">

                    Submit Issue

                </button>

            </form>

        </div>

    );

}

export default ReportIssue;