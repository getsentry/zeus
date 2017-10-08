const makeError = (className, defaultCode = null, baseClass = Error) => {
  function newError(msg, code = defaultCode) {
    this.message = msg;
    this.code = code;
    this.name = className;
    const err = baseClass(msg);
    this.stack = err.stack;
  }
  newError.prototype = Object.create(baseClass.prototype);
  newError.prototype.constructor = newError;
  return newError;
};

const ApiError = makeError('ApiError');
const Error404 = makeError('Error404', 404, ApiError);
const Error401 = makeError('Error401', 401, ApiError);

export {ApiError, Error401, Error404};
