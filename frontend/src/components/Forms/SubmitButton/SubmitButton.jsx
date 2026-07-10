import "./SubmitButton.css";

function SubmitButton({
    text,
    loading = false
}) {

    return (

        <button
            className="submit-button"
            disabled={loading}
        >

            {loading ? "Processing..." : text}

        </button>

    );

}

export default SubmitButton;