function PaintCalculator() {

    const paintLiters = 220;
    const pricePerLiter = 340;

    const totalCost = paintLiters * pricePerLiter;

    return `

        <div class="material-card">

            <h2>Paint Calculation</h2>

            <p>
                Paint Required:
                ${paintLiters} Liters
            </p>

            <p>
                Price Per Liter:
                ₹${pricePerLiter}
            </p>

            <p>
                Total Paint Cost:
                ₹${totalCost}
            </p>

        </div>

    `;
}

export default PaintCalculator;