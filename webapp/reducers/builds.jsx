import {
  ADD_BUILD,
  LOAD_BUILD_LIST,
  PRE_LOAD_BUILD_LIST,
  REMOVE_BUILD,
  UPDATE_BUILD
} from '../types';

const initialState = {
  items: [],
  loaded: false
};

export default (state = initialState, action = {}) => {
  switch (action.type) {
    case ADD_BUILD:
      return {
        ...state,
        items: [action.payload, ...state.items]
      };
    // this should arguably dedupe to ensure correctness
    case PRE_LOAD_BUILD_LIST:
      return {
        ...state,
        loaded: false
      };
    case LOAD_BUILD_LIST:
      return {
        ...state,
        items: [...action.items],
        loaded: true
      };
    case REMOVE_BUILD:
      return {
        ...state,
        items: [...state.items.filter(m => m.id !== action.id)]
      };
    case UPDATE_BUILD:
      return {
        ...state,
        items: [
          ...state.items.map(m => {
            if (m.id !== action.payload.id) {
              return {...m, ...action.payload};
            }
            return m;
          })
        ]
      };
    default:
      return state;
  }
};
