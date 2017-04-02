import { browserHistory } from 'react-router';

import {
  LOGIN_USER_SUCCESS,
  LOGIN_USER_FAILURE,
  LOGIN_USER_REQUEST,
  LOGOUT_USER,
  REGISTER_USER_FAILURE,
  REGISTER_USER_REQUEST,
  REGISTER_USER_SUCCESS,
} from './enum';

import { createUser, getToken, parseJSON } from '../utils/common';


export function loginUserRequest() {
  return {
    type: LOGIN_USER_REQUEST,
  };
}

export function loginUserSuccess(token) {
  localStorage.setItem('token', token);
  return {
    type: LOGIN_USER_SUCCESS,
    payload: {
      token,
    },
  };
}

export function loginUserFailure(error) {
  localStorage.removeItem('token');
  return {
    type: LOGIN_USER_FAILURE,
    payload: {
      status: error.status,
    },
  };
}

export function logout() {
  localStorage.removeItem('token');
  return {
    type: LOGOUT_USER,
  };
}

export function logoutAndRedirect() {
  return (dispatch) => {
    dispatch(logout());
    browserHistory.push('/');
  };
}

export function redirectToRoute(route) {
  return () => {
    browserHistory.push(route);
  };
}

export function loginUser(email, password) {
  return (dispatch) => {
    dispatch(loginUserRequest());
    return getToken(email, password)
      .then(parseJSON)
      .then((response) => {
        try {
          dispatch(loginUserSuccess(response.token));
          browserHistory.push('/main');
        } catch (e) {
          dispatch(loginUserFailure({
            response: {
              status: 403,
              statusText: 'Invalid token',
            },
          }));
        }
      })
      .catch((error) => {
        dispatch(loginUserFailure(error));
      });
  };
}

export function registerUserRequest() {
  return {
    type: REGISTER_USER_REQUEST,
  };
}

export function registerUserSuccess(token) {
  localStorage.setItem('token', token);
  return {
    type: REGISTER_USER_SUCCESS,
    payload: {
      token,
    },
  };
}

export function registerUserFailure(error) {
  localStorage.removeItem('token');
  return {
    type: REGISTER_USER_FAILURE,
    payload: {
      status: error.status,
      statusText: error.statusText,
    },
  };
}

export function registerUser(email, password) {
  return function (dispatch) {
    dispatch(registerUserRequest());
    return createUser(email, password)
      .then(parseJSON)
      .then((response) => {
        try {
          dispatch(registerUserSuccess(response.token));
          browserHistory.push('/main');
        } catch (e) {
          dispatch(registerUserFailure({
            response: {
              status: 403,
              statusText: 'Invalid token',
            },
          }));
        }
      })
      .catch((error) => {
        dispatch(registerUserFailure(error));
      });
  };
}
