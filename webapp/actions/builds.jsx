import api from '../api';
import {
  ADD_BUILD,
  LOAD_BUILD_LIST,
  PRE_LOAD_BUILD_LIST,
  REMOVE_BUILD,
  UPDATE_BUILD
} from '../types';

export const addBuild = payload => {
  return dispatch => {
    return dispatch({
      type: ADD_BUILD,
      payload
    });
  };
};

export const removeBuild = id => {
  return dispatch => {
    return dispatch({
      type: REMOVE_BUILD,
      id
    });
  };
};

export const updateBuild = payload => {
  return dispatch => {
    return dispatch({
      type: UPDATE_BUILD,
      payload
    });
  };
};

export const loadBuilds = items => {
  return dispatch => {
    dispatch({
      type: LOAD_BUILD_LIST,
      items
    });
  };
};

export const loadBuildsForRepository = (repoFullName, query, emptyState = true) => {
  return dispatch => {
    if (emptyState) {
      dispatch({
        type: PRE_LOAD_BUILD_LIST
      });
    }
    api
      .get(`/repos/${repoFullName}/builds`, {
        query
      })
      .then(items => {
        dispatch({
          type: LOAD_BUILD_LIST,
          items
        });
      });
  };
};

export const loadBuildsForUser = (userID = 'me') => {
  return dispatch => {
    api.get(`/users/${userID}/builds`).then(items => {
      dispatch({
        type: LOAD_BUILD_LIST,
        items
      });
    });
  };
};
