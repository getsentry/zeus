import {ADD_REPO, LOAD_REPO_LIST, REMOVE_REPO, UPDATE_REPO} from '../actions/types';

import {sortBy} from 'lodash';

const initialState = {
  items: [],
  loaded: false
};

export default (state = initialState, action = {}) => {
  switch (action.type) {
    case ADD_REPO:
      return {
        ...state,
        items: sortBy([...state.items, action.payload], ['ownerName', 'name'])
      };
    // this should arguably dedupe to ensure correctness
    case LOAD_REPO_LIST:
      return {
        ...state,
        items: sortBy([...action.items], ['ownerName', 'name']),
        loaded: true
      };
    case REMOVE_REPO:
      return {
        ...state,
        items: [...state.items.filter(m => m.id !== action.id)]
      };
    case UPDATE_REPO:
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
