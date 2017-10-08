class ApiError extends Error {}
class Error401 extends ApiError {
  static code = 401;
}
class Error404 extends Error {
  static code = 404;
}

export {ApiError, Error401, Error404};
