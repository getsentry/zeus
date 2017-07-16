export class Request {
  static UNSET = 0;
  static OPENED = 1;
  static HEADERS_RECEIVED = 2;
  static LOADING = 3;
  static DONE = 4;

  static OK = 200;

  constructor(params, resolve, reject) {
    let contentType = params.contentType || 'application/json';

    this.alive = true;

    let xhr = new XMLHttpRequest();

    // bind xhr so we can abort later
    this.xhr = xhr;

    xhr.open(params.method || 'GET', params.url);
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    xhr.setRequestHeader('Accept', 'application/json; charset=utf-8');
    xhr.setRequestHeader('Content-Type', contentType);
    Object.keys(params.headers || {}).forEach(key => {
      xhr.setRequestHeader(key, params.headers[key]);
    });
    xhr.send(params.data ? JSON.stringify(params.data) : null);

    xhr.onreadystatechange = () => {
      if (xhr.readyState === Request.DONE) {
        let responseData = this.processResponseText(xhr);
        if (xhr.status >= 200 && xhr.status < 300) {
          responseData.xhr = xhr;
          resolve(responseData);
        } else {
          let error = new Error(xhr.responseText);
          error.data = responseData;
          error.xhr = xhr;
          reject(error);
        }
      }
    };
  }

  processResponseText(xhr) {
    let contentType = xhr.getResponseHeader('content-type');
    if (contentType && contentType.split(';')[0].split('/')[1] === 'json') {
      try {
        return JSON.parse(xhr.responseText);
      } catch (ex) {
        console.error(ex);
      }
    }
    return xhr.responseText;
  }

  cancel() {
    this.alive = false;
    this.xhr.abort();
  }
}

/**
 * Converts input parameters to API-compatible query arguments
 * @param params
 */
export function paramsToQueryArgs(params) {
  return params.itemIds
    ? {id: params.itemIds} // items matching array of itemids
    : params.query
      ? {query: params.query} // items matching search query
      : undefined; // all items
}

export class Client {
  constructor(options) {
    if (options === undefined) {
      options = {};
    }
    this.baseUrl = options.baseUrl || '/api';
    this.activeRequests = {};
  }

  uniqueId() {
    let s4 = () => {
      return Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1);
    };
    return s4() + s4() + '-' + s4() + '-' + s4() + '-' + s4() + '-' + s4() + s4() + s4();
  }

  clear() {
    for (let id in this.activeRequests) {
      this.activeRequests[id].cancel();
    }
  }

  request(path, options = {}) {
    let query = window.encodeURIComponent(options.query || '');
    let method = options.method || (options.data ? 'POST' : 'GET');
    let data = options.data;
    let id = this.uniqueId();

    let fullUrl;
    if (path.indexOf(this.baseUrl) === -1) {
      fullUrl = this.baseUrl + path;
    } else {
      fullUrl = path;
    }
    if (query) {
      if (fullUrl.indexOf('?') !== -1) {
        fullUrl += '&' + query;
      } else {
        fullUrl += '?' + query;
      }
    }

    return new Promise((resolve, reject) => {
      let request = new Request(
        {
          url: fullUrl,
          method: method,
          data: data
        },
        resolve,
        reject
      );
      this.activeRequests[id] = request;
    });
  }

  get(path, options = {}) {
    return this.request(path, {
      method: 'GET',
      ...options
    });
  }

  post(path, options = {}) {
    return this.request(path, {
      method: 'POST',
      ...options
    });
  }

  delete(path, options = {}) {
    return this.request(path, {
      method: 'DELETE',
      ...options
    });
  }

  put(path, options = {}) {
    return this.request(path, {
      method: 'PUT',
      ...options
    });
  }
}

export default new Client();
