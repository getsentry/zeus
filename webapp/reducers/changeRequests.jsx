import {LOAD_CHANGE_REQUEST_LIST, PRE_LOAD_CHANGE_REQUEST_LIST} from '../types';

const initialState = {
  items: [],
  links: {},
  loaded: false
};

export default (state = initialState, action = {}) => {
  switch (action.type) {
    case PRE_LOAD_CHANGE_REQUEST_LIST:
      return {
        ...state,
        loaded: false
      };
    case LOAD_CHANGE_REQUEST_LIST:
      return {
        ...state,
        items: [...action.items],
        links: {...action.items.links},
        loaded: true
      };
    default:
      return state;
  }
};
