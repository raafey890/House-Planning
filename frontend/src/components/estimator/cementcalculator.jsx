function CementCalculator() {

    const cementBags = 320;
    const pricePerBag = 420;

    const totalCost = cementBags * pricePerBag;

    return `

        <div class="material-card">

            <h2>Cement Calculation</h2>

            <p>
                Cement Bags Required:
                ${cementBags}
            </p>

            <p>
                Price Per Bag:
                ₹${pricePerBag}
            </p>

            <p>
                Total Cement Cost:
                ₹${totalCost}
            </p>

        </div>

    `;
}

export default CementCalculator;