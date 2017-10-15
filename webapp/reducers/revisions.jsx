import {
  ADD_REVISION,
  LOAD_REVISION_LIST,
  PRE_LOAD_REVISION_LIST,
  REMOVE_REVISION,
  UPDATE_REVISION
} from '../actions/types';

const initialState = {
  items: [],
  loaded: false
};

export default (state = initialState, action = {}) => {
  switch (action.type) {
    case ADD_REVISION:
      return {
        ...state,
        items: [action.payload, ...state.items]
      };
    // this should arguably dedupe to ensure correctness
    case PRE_LOAD_REVISION_LIST:
      return {
        ...state,
        loaded: false
      };
    case LOAD_REVISION_LIST:
      return {
        ...state,
        items: [...action.items],
        loaded: true
      };
    case REMOVE_REVISION:
      return {
        ...state,
        items: [...state.items.filter(m => m.id !== action.id)]
      };
    case UPDATE_REVISION:
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
