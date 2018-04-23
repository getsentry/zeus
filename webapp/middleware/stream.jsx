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
  let channelRefs = {
    // ref: count
  };

  /**
   * Close the connection and cleanup
   */
  const closeStream = store => {
    if (stream) {
      console.info(`Closing connection to ${stream.url} ...`);
      stream.close();
      stream = null;
    }
  };

  const ensureStream = store => {
    if (stream) {
      closeStream(store);
    }
    if (!config.token) {
      console.info('No token available for stream');
      return;
    }
    if (config.channels.length === 0) {
      console.info('No channel subscriptions for stream');
      return;
    }

    stream = new EventSource(
      `${window.ZEUS_PUBSUB_ENDPOINT}?token=${
        config.token
      }&channels=${window.encodeURIComponent(config.channels.join(','))}`
    );

    console.info(`Opening connection to ${stream.url}`);

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
    ensureStream(store);
  };

  const addChannels = (store, channels) => {
    channels.forEach(c => {
      if (channelRefs[c]) {
        channelRefs[c] += 1;
      } else {
        channelRefs[c] = 1;
      }
    });
    config.channels = [...config.channels, ...channels].filter(c => !!channelRefs[c]);
    console.info('Subscription changed', config.channels);
    ensureStream(store);
  };

  const removeChannels = (store, channels) => {
    channels.forEach(c => {
      if (channelRefs[c] > 1) {
        channelRefs[c] -= 1;
      } else if (channelRefs[c]) {
        delete channelRefs[c];
      }
    });
    config.channels = [...config.channels, ...channels].filter(c => !!channelRefs[c]);
    console.info('Subscription changed', config.channels);
    ensureStream(store);
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
        addChannels(store, action.payload.channels);
        next(action);
        break;

      case STREAM_UNSUBSCRIBE:
        removeChannels(store, action.payload.channels);
        next(action);
        break;

      default:
        next(action);
    }
  };
};

export default createMiddleware();
