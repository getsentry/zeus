function Error404(msg) {
  this.message = msg;
  this.code = 404;
  this.name = 'Error404';
  const err = Error(msg);
  this.stack = err.stack;
}

Error404.prototype = Object.create(Error.prototype);
Error404.prototype.constructor = Error404;

export {Error404};
