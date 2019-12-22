import api from '../api';
import {LOAD_CHANGE_REQUEST_LIST, PRE_LOAD_CHANGE_REQUEST_LIST} from '../types';

export const fetchChangeRequests = query => {
  return dispatch => {
    dispatch({
      type: PRE_LOAD_CHANGE_REQUEST_LIST
    });
    api
      .get(`/change-requests`, {
        query
      })
      .then(items => {
        dispatch({
          type: LOAD_CHANGE_REQUEST_LIST,
          items
        });
      });
  };
};
