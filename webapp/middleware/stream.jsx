import {compose} from 'redux';
import partial from 'lodash/fp/partial';

import {open, error, message} from '../actions/stream';
import {STREAM_CONNECT, STREAM_DISCONNECT} from '../types';

const createMiddleware = () => {
  // Hold a reference to the EventSource instance in use.
  let stream;

  /**
   * Create the EventSource object and attach the standard callbacks
   */
  const initialize = ({dispatch}, config) => {
    stream = new EventSource(`${window.ZEUS_PUBSUB_ENDPOINT}?token=${config.token}`);

    // Function will dispatch actions returned from action creators.
    const dispatchAction = partial(compose, [dispatch]);

    // Setup handlers to be called like this:
    // dispatch(open(event));
    stream.onopen = dispatchAction(open);
    stream.onerror = dispatchAction(error);
    stream.onmessage = dispatchAction(message);
  };

  /**
   * Close the connection and cleanup
   */
  const close = () => {
    if (stream) {
      console.warn(`Closing connection to ${stream.url} ...`);
      stream.close();
      stream = null;
    }
  };

  /**
   * The primary Redux middleware function.
   * Each of the actions handled are user-dispatched.
   */
  return store => next => action => {
    switch (action.type) {
      // User request to connect
      case STREAM_CONNECT:
        close();
        initialize(store, action.payload);
        next(action);
        break;

      // User request to disconnect
      case STREAM_DISCONNECT:
        close();
        next(action);
        break;

      default:
        next(action);
    }
  };
};

export default createMiddleware();
