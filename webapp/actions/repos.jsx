import api from '../api';
import {ADD_REPO, LOAD_REPO_LIST, REMOVE_REPO, UPDATE_REPO} from '../types';

export const addRepo = payload => {
  return dispatch => {
    return dispatch({
      type: ADD_REPO,
      payload
    });
  };
};

export const removeRepo = id => {
  return dispatch => {
    return dispatch({
      type: REMOVE_REPO,
      id
    });
  };
};

export const updateRepo = payload => {
  return dispatch => {
    return dispatch({
      type: UPDATE_REPO,
      payload
    });
  };
};

export const loadRepos = () => {
  return dispatch => {
    return api
      .get('/repos')
      .then(items => {
        dispatch({
          type: LOAD_REPO_LIST,
          items
        });
      })
      .catch(err => {
        if (err.xhr.status == 401) {
          dispatch({
            type: LOAD_REPO_LIST,
            items: []
          });
        } else {
          throw err;
        }
      });
  };
};
