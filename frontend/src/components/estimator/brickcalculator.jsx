function BrickCalculator() {

    const bricks = 25000;
    const brickPrice = 12;

    const totalCost = bricks * brickPrice;

    return `

        <div class="material-card">

            <h2>Brick Calculation</h2>

            <p>
                Bricks Required:
                ${bricks}
            </p>

            <p>
                Price Per Brick:
                ₹${brickPrice}
            </p>

            <p>
                Total Brick Cost:
                ₹${totalCost}
            </p>

        </div>

    `;
}

export default BrickCalculator;