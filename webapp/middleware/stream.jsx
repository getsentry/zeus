import {compose} from 'redux';
import partial from 'lodash/fp/partial';

import {open, error, message} from '../actions/stream';
import {
  STREAM_CONNECT,
  STREAM_DISCONNECT,
  STREAM_SUBSCRIBE,
  STREAM_UNSUBSCRIBE
} from '../types';

const createMiddleware = () => {
  // Hold a reference to the EventSource instance in use.
  let stream;
  let config = {
    channels: [],
    token: null
  };

  /**
   * Close the connection and cleanup
   */
  const closeStream = store => {
    if (stream) {
      console.warn(`Closing connection to ${stream.url} ...`);
      stream.close();
      stream = null;
    }
  };

  const openStream = store => {
    if (stream) {
      closeStream(store);
    }
    if (!config.token) {
      return;
    }
    if (config.channels.length === 0) {
      return;
    }

    stream = new EventSource(
      `${window.ZEUS_PUBSUB_ENDPOINT}?token=${config.token}&channels=${window.encodeURIComponent(
        config.channels.join(',')
      )}`
    );

    // Function will dispatch actions returned from action creators.
    const dispatchAction = partial(compose, [store.dispatch]);

    // Setup handlers to be called like this:
    // dispatch(open(event));
    stream.onopen = dispatchAction(open);
    stream.onerror = dispatchAction(error);
    stream.onmessage = dispatchAction(message);
  };

  /**
   * Create the EventSource object and attach the standard callbacks
   */
  const initializeStream = (store, payload) => {
    config.token = payload.token;
    openStream(store);
  };

  const changeSubscription = channels => {
    config.channels = channels;
    closeStream();
    openStream();
  };

  /**
   * The primary Redux middleware function.
   * Each of the actions handled are user-dispatched.
   */
  return store => next => action => {
    switch (action.type) {
      // User request to connect
      case STREAM_CONNECT:
        closeStream(store);
        initializeStream(store, action.payload);
        next(action);
        break;

      // User request to disconnect
      case STREAM_DISCONNECT:
        closeStream(store);
        next(action);
        break;

      case STREAM_SUBSCRIBE:
      case STREAM_UNSUBSCRIBE:
        changeSubscription(store, action.payload.channels);
        next(action);
        break;

      default:
        next(action);
    }
  };
};

export default createMiddleware();
