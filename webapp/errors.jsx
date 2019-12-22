class ApiError extends Error {
  constructor(msg, code) {
    super(msg);
    this.code = code;
  }
}

class ResourceNotFound extends Error {
  static code = 404;
}

class NetworkError extends Error {
  constructor(msg, code) {
    super(msg);
    this.code = code;
  }
}

export {ApiError, ResourceNotFound, NetworkError};
