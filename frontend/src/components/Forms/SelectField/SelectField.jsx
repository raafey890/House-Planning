import "./SelectField.css";

function SelectField({
    label,
    options = [],
    value,
    onChange
}) {

    return (

        <div className="select-field-group">

            {label && (

                <label className="select-label">

                    {label}

                </label>

            )}

            <select
                value={value}
                onChange={onChange}
                className="select-field"
            >

                {options.map((option, index) => (

                    <option
                        key={index}
                        value={option.value}
                    >

                        {option.label}

                    </option>

                ))}

            </select>

        </div>

    );

}

export default SelectField;