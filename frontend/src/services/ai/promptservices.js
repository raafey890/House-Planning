function promptService(userData) {

    const prompt = `

    Generate a realistic modern house.

    Plot Size:
    ${userData.plotSize}

    Facing:
    ${userData.facing}

    Floors:
    ${userData.floors}

    Bedrooms:
    ${userData.rooms}

    Budget:
    ${userData.budget}

    Style:
    ${userData.style}

    Include:
    luxury interiors,
    modern elevation,
    parking,
    balcony,
    realistic textures,
    ultra realistic 2K render.

    `;

    return prompt;
}

export default promptService;