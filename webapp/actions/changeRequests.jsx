import api from '../api';
import {LOAD_CHANGE_REQUEST_LIST, PRE_LOAD_CHANGE_REQUEST_LIST} from '../types';

export const loadChangeRequestsForRepository = (repoFullName, query) => {
  return dispatch => {
    dispatch({
      type: PRE_LOAD_CHANGE_REQUEST_LIST
    });
    api
      .get(`/repos/${repoFullName}/change-requests`, {
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

export const loadChangeRequestsForUser = (userID = 'me', query) => {
  return dispatch => {
    api.get(`/users/${userID}/change-requests`, {query}).then(items => {
      dispatch({
        type: LOAD_CHANGE_REQUEST_LIST,
        items
      });
    });
  };
};
