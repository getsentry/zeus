import api from '../api';
import {
  ADD_REVISION,
  LOAD_REVISION_LIST,
  PRE_LOAD_REVISION_LIST,
  REMOVE_REVISION,
  UPDATE_REVISION
} from '../types';

export const addRevision = payload => {
  return dispatch => {
    return dispatch({
      type: ADD_REVISION,
      payload
    });
  };
};

export const removeRevision = id => {
  return dispatch => {
    return dispatch({
      type: REMOVE_REVISION,
      id
    });
  };
};

export const updateRevision = payload => {
  return dispatch => {
    return dispatch({
      type: UPDATE_REVISION,
      payload
    });
  };
};

export const loadRevisions = items => {
  return dispatch => {
    dispatch({
      type: LOAD_REVISION_LIST,
      items
    });
  };
};

export const loadRevisionsForRepository = (repoFullName, query, emptyState = true) => {
  return dispatch => {
    if (emptyState) {
      dispatch({
        type: PRE_LOAD_REVISION_LIST
      });
    }
    api
      .get(`/repos/${repoFullName}/revisions`, {
        query
      })
      .then(items => {
        dispatch({
          type: LOAD_REVISION_LIST,
          items
        });
      });
  };
};
