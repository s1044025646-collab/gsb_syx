const errorHandler = (err, req, res, next) => {
  const statusCode = res.statusCode === 200 ? 500 : res.statusCode;

  res.status(statusCode).json({
    msg: err.message || 'Server Error',
  });
};

const notFound = (req, res) => {
  res.status(404).json({
    msg: 'Route not found',
  });
};

module.exports = { errorHandler, notFound };
