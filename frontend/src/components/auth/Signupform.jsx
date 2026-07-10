function SignupForm() {

    return `

        <section class="signup-section">

            <h2>
                Create Account
            </h2>

            <form class="signup-form">

                <input
                type="text"
                placeholder="Full Name"
                >

                <input
                type="email"
                placeholder="Enter Email"
                >

                <input
                type="password"
                placeholder="Create Password"
                >

                <button>
                    Signup
                </button>

            </form>

        </section>

    `;
}

export default SignupForm;