import {ADD_INDICATOR, REMOVE_INDICATOR} from '../types';

let _lastId = 1;

const _addIndicator = payload => {
  return {
    type: ADD_INDICATOR,
    payload
  };
};

const _removeIndicator = id => {
  return {
    type: REMOVE_INDICATOR,
    id
  };
};

export const addIndicator = (message, type, expiresAfter = 0) => {
  return dispatch => {
    let payload = {
      message,
      type,
      expiresAfter,
      id: _lastId++
    };
    dispatch(_addIndicator(payload));

    if (expiresAfter > 0) {
      setTimeout(() => {
        dispatch(_removeIndicator(payload.id));
      }, expiresAfter);
    }

    return payload;
  };
};

export const removeIndicator = indicator => {
  return dispatch => {
    dispatch(_removeIndicator(indicator.id));
  };
};
