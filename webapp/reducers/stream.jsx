import {SET_STREAM_TOKEN} from '../types';

const initialState = {
  token: null
};

export default (state = initialState, action = {}) => {
  switch (action.type) {
    case SET_STREAM_TOKEN:
      return {...state, token: action.payload.token};
    default:
      return state;
  }
};
