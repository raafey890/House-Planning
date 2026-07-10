function PlannerForm() {

    return `

        <form class="planner-form">

            <h2>
                House Planning Form
            </h2>

            <input
            type="text"
            placeholder="Enter Plot Size (30x40)"
            >

            <input
            type="number"
            placeholder="Enter Budget"
            >

            <button>
                Generate AI Designs
            </button>

        </form>

    `;
}

export default PlannerForm;