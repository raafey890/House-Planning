import "./Input.css";

function Input({
    label,
    type = "text",
    placeholder,
    value,
    onChange,
    error
}) {

    return (

        <div className="input-group">

            {label && (

                <label className="input-label">

                    {label}

                </label>

            )}

            <input
                type={type}
                placeholder={placeholder}
                value={value}
                onChange={onChange}
                className="custom-input"
            />

            {error && (

                <p className="input-error">

                    {error}

                </p>

            )}

        </div>

    );

}

export default Input; 