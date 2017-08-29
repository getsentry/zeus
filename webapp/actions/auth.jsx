import api from '../api';
import {SET_CURRENT_AUTH, SET_STREAM_TOKEN} from '../types';

export function setAuth(payload) {
  return {
    type: SET_CURRENT_AUTH,
    payload
  };
}

export function logout() {
  return dispatch => {
    api.delete('/auth').then(() => {
      localStorage.removeItem('auth');
      dispatch(setAuth({isAuthenticated: false, user: null}));
    });
  };
}

export function authSession() {
  return dispatch => {
    return api.get('/auth').then(
      data => {
        if (data.isAuthenticated) {
          localStorage.setItem('auth', data);
        } else {
          localStorage.removeItem('auth');
        }
        dispatch(setAuth(data));
        dispatch({
          type: SET_STREAM_TOKEN,
          payload: {
            timestamp: new Date(),
            token: data.getResponseHeader('X-Stream-Token')
          }
        });
      },
      error => {
        localStorage.removeItem('auth');
        dispatch(setAuth({isAuthenticated: false, user: null}));
      }
    );
  };
}
