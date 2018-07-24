class ApiError extends Error {
  constructor(msg, code) {
    super(msg);
    this.code = code;
  }
}

class ResourceNotFound extends ApiError {
  static code = 404;
}

class NetworkError extends ApiError {}

export {ApiError, ResourceNotFound, NetworkError};
