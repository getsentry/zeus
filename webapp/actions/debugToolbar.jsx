import api from '../api';
import {ADD_DEBUG_ENTRY, CLEAR_DEBUG_ENTRIES} from '../types';

export const addDebugEntry = payload => {
  return dispatch => {
    return dispatch({
      type: ADD_DEBUG_ENTRY,
      payload
    });
  };
};

export const clearDebugEntries = id => {
  return dispatch => {
    return dispatch({
      type: CLEAR_DEBUG_ENTRIES,
      id
    });
  };
};
