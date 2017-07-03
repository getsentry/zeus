// import axios from 'axios';
// import setAuthorizationToken from '../utils/setAuthorizationToken';
// import jwtDecode from 'jwt-decode';
import {SET_CURRENT_USER} from './types';

export function setCurrentUser(user) {
  return {
    type: SET_CURRENT_USER,
    user
  };
}

export function logout() {
  return dispatch => {
    api.logout();
    // localStorage.removeItem('jwtToken');
    // setAuthorizationToken(false);
    dispatch(setCurrentUser({}));
  };
}

export function login(data) {
  return dispatch => {
    return api.post('/api/auth', data).then(res => {
      //   localStorage.setItem('jwtToken', token);
      //   setAuthorizationToken(token);
      dispatch(setCurrentUser(res.data));
    });
  };
}
