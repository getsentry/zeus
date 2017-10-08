class ApiError extends Error {}
class ResourceNotFound extends Error {
  static code = 404;
}

export {ApiError, ResourceNotFound};
