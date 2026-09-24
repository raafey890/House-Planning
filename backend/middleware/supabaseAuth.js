const jwt = require("jsonwebtoken");

const protect = async (req, res, next) => {
    let token;
    
    if (req.headers.authorization && req.headers.authorization.startsWith("Bearer")) {
        try {
            token = req.headers.authorization.split(" ")[1];
            
            if (!process.env.SUPABASE_JWT_SECRET) {
                console.error("Missing SUPABASE_JWT_SECRET environment variable");
                return res.status(500).json({ message: "Server configuration error" });
            }

            const decoded = jwt.verify(token, process.env.SUPABASE_JWT_SECRET);
            
            // Supabase payload structure usually contains sub (which is the user id)
            req.user = {
                id: decoded.sub,
                email: decoded.email,
                role: decoded.role
            };

            next();
        } catch (error) {
            console.error("JWT Verification failed:", error.message);
            res.status(401).json({ message: "Not authorized, token failed" });
        }
    } else {
        res.status(401).json({ message: "Not authorized, no token" });
    }
};

module.exports = { protect };
