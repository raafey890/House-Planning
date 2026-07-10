const errorResponse = (
  res,
  message,
  statusCode = 500,
  error = null
) => {
  return res.status(statusCode).json({
    success: false,
    message,
    timestamp: new Date(),
    error:
      process.env.NODE_ENV === "development"
        ? error
        : undefined,
  });
};

module.exports = errorResponse;