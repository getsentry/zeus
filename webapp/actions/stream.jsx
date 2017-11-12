import {
  STREAM_CONNECT,
  STREAM_OPEN,
  STREAM_ERROR,
  STREAM_MESSAGE,
  STREAM_SUBSCRIBE,
  STREAM_UNSUBSCRIBE
} from '../types';

export const connect = token => ({
  type: STREAM_CONNECT,
  payload: {
    timestamp: new Date(),
    token
  }
});

export const subscribe = channels => ({
  type: STREAM_SUBSCRIBE,
  payload: {
    timestamp: new Date(),
    channels
  }
});

export const unsubscribe = channels => ({
  type: STREAM_UNSUBSCRIBE,
  payload: {
    timestamp: new Date(),
    channels
  }
});

export const open = event => ({
  type: STREAM_OPEN,
  payload: {
    timestamp: new Date(),
    event
  }
});

export const error = event => ({
  type: STREAM_ERROR,
  payload: {
    timestamp: new Date(),
    event
  }
});

export const message = event => ({
  type: STREAM_MESSAGE,
  payload: {
    timestamp: new Date(),
    data: event.data,
    event
  }
});
