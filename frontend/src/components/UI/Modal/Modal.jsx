import "./Modal.css";

function Modal({
    isOpen,
    onClose,
    title,
    children
}) {

    if (!isOpen) return null;

    return (

        <div className="modal-overlay">

            <div className="modal-box">

                <div className="modal-header">

                    <h2>
                        {title}
                    </h2>

                    <button
                        className="modal-close-button"
                        onClick={onClose}
                    >
                        ×
                    </button>

                </div>

                <div className="modal-content">

                    {children}

                </div>

            </div>

        </div>

    );

}

export default Modal;