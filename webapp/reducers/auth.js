import {SET_CURRENT_AUTH} from '../actions/types';

const initialState = {
  // default to unknown state
  isAuthenticated: null,
  user: null
};

export default (state = initialState, action = {}) => {
  switch (action.type) {
    case SET_CURRENT_AUTH:
      return {...state, ...action.data};
    default:
      return state;
  }
};
