function LoginForm() {

    return `

        <section class="login-section">

            <h2>
                User Login
            </h2>

            <form class="login-form">

                <input
                type="email"
                placeholder="Enter Email"
                >

                <input
                type="password"
                placeholder="Enter Password"
                >

                <button>
                    Login
                </button>

            </form>

        </section>

    `;
}

export default LoginForm;