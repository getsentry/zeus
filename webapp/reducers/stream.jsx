import {STREAM_CONNECT, STREAM_SUBSCRIBE, STREAM_UNSUBSCRIBE} from '../types';

const initialState = {
  token: null
};

export default (state = initialState, action = {}) => {
  switch (action.type) {
    case STREAM_CONNECT:
      return {...state, token: action.payload.token};
    case STREAM_SUBSCRIBE:
      return {
        ...state,
        channels: [...(state.channels || []), ...action.payload.channels]
      };
    case STREAM_UNSUBSCRIBE:
      return {
        ...state,
        channels: [
          ...(state.channels || []).filter(c => action.payload.channels.indexOf(c) === -1)
        ]
      };
    default:
      return state;
  }
};
