import React from "react";

const BudgetSummary = () => {

    return (

        <div className="budget-summary">

            <h2>Total Budget Summary</h2>

            <div className="budget-cards">

                <div className="budget-card">

                    <h3>Total Cost</h3>

                    <h1>₹25,00,000</h1>

                </div>

                <div className="budget-card">

                    <h3>Material Cost</h3>

                    <h1>₹15,00,000</h1>

                </div>

                <div className="budget-card">

                    <h3>Labor Cost</h3>

                    <h1>₹10,00,000</h1>

                </div>

            </div>

        </div>

    );

};

export default BudgetSummary;