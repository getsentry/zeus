import {ADD_DEBUG_ENTRY, CLEAR_DEBUG_ENTRIES} from '../types';

const initialState = {
  items: []
};

export default (state = initialState, action = {}) => {
  switch (action.type) {
    case ADD_DEBUG_ENTRY:
      return {
        ...state,
        items: [action.payload, ...state.items]
      };
    case CLEAR_DEBUG_ENTRIES:
      return {
        ...state,
        items: []
      };
    default:
      return state;
  }
};
