import {STREAM_CONNECT} from '../types';

const initialState = {
  token: null
};

export default (state = initialState, action = {}) => {
  switch (action.type) {
    case STREAM_CONNECT:
      return {...state, token: action.payload.token};
    default:
      return state;
  }
};
