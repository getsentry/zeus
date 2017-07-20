import {ADD_BUILD, LOAD_BUILD_LIST, REMOVE_BUILD, UPDATE_BUILD} from '../actions/types';

import {sortBy} from 'lodash';

const initialState = {
  items: [],
  loaded: false
};

export default (state = initialState, action = {}) => {
  switch (action.type) {
    case ADD_BUILD:
      return {
        ...state,
        items: sortBy([...state.items, action.payload], ['createdAt']).reverse()
      };
    // this should arguably dedupe to ensure correctness
    case LOAD_BUILD_LIST:
      return {
        ...state,
        items: sortBy([...action.items], ['createdAt']).reverse(),
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
