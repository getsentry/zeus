import api from '../api';
import {SET_CURRENT_AUTH} from './types';

export function setAuth(data) {
  return {
    type: SET_CURRENT_AUTH,
    data
  };
}

export function logout() {
  return dispatch => {
    api.delete('/auth').then(() => {
      localStorage.removeItem('auth');
      dispatch(setAuth({}));
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
      },
      error => {
        dispatch(setAuth({isAuthenticated: false, user: null}));
      }
    );
  };
}
