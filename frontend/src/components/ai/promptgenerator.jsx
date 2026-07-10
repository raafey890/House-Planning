function PromptGenerator(userData) {

    const prompt = `

    Generate a realistic modern Indian house.

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
    luxury elevation,
    modern balcony,
    parking area,
    natural lighting,
    realistic materials,
    ultra realistic 2K render.

    `;

    return prompt;
}

export default PromptGenerator;