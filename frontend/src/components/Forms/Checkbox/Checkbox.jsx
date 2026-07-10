import "./Checkbox.css";

function Checkbox({
    label,
    checked,
    onChange
}) {

    return (

        <label className="checkbox-group">

            <input
                type="checkbox"
                checked={checked}
                onChange={onChange}
            />

            {label}

        </label>

    );

}

export default Checkbox;