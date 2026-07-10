import "./FormInput.css";

function FormInput({
    label,
    type = "text",
    placeholder,
    value,
    onChange,
    error
}) {

    return (

        <div className="form-input-group">

            {label && (

                <label className="form-label">

                    {label}

                </label>

            )}

            <input
                type={type}
                placeholder={placeholder}
                value={value}
                onChange={onChange}
                className="form-input"
            />

            {error && (

                <p className="form-error">

                    {error}

                </p>

            )}

        </div>

    );

}

export default FormInput;