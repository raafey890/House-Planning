import "./TextArea.css";

function TextArea({
    label,
    placeholder,
    value,
    onChange
}) {

    return (

        <div className="textarea-group">

            {label && (

                <label className="textarea-label">

                    {label}

                </label>

            )}

            <textarea
                placeholder={placeholder}
                value={value}
                onChange={onChange}
                className="custom-textarea"
            />

        </div>

    );

}

export default TextArea;