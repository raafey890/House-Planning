function SteelCalculator() {

    const steelWeight = 4500;
    const steelPrice = 72;

    const totalCost = steelWeight * steelPrice;

    return `

        <div class="material-card">

            <h2>Steel Calculation</h2>

            <p>
                Steel Required:
                ${steelWeight} KG
            </p>

            <p>
                Price Per KG:
                ₹${steelPrice}
            </p>

            <p>
                Total Steel Cost:
                ₹${totalCost}
            </p>

        </div>

    `;
}

export default SteelCalculator;