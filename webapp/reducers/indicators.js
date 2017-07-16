import {ADD_INDICATOR, REMOVE_INDICATOR} from '../actions/types';

const initialState = {
  items: []
};

export default (state = initialState, action = {}) => {
  switch (action.type) {
    case ADD_INDICATOR:
      return {
        ...state,
        items: [...state.items, action.payload]
      };
    case REMOVE_INDICATOR:
      return {
        ...state,
        items: [...state.items.filter(m => m.id !== action.id)]
      };
    default:
      return state;
  }
};
