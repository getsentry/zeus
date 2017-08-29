import {SET_STREAM_TOKEN, STREAM_OPEN, STREAM_ERROR, STREAM_MESSAGE} from '../types';

export function setStreamToken(token) {
  return {
    type: SET_STREAM_TOKEN,
    payload: {
      timestmap: new Date(),
      token
    }
  };
}

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
