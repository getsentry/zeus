import {SET_CURRENT_AUTH} from '../types';

import * as Sentry from '@sentry/browser';

const createMiddleware = Sentry => {
  return () => next => action => {
    if (action.type === SET_CURRENT_AUTH) {
      let {isAuthenticated, user} = action.payload;
      if (!isAuthenticated) {
        Sentry.setUser(null);
      } else {
        Sentry.setUser({
          id: user.id,
          email: user.email
        });
      }
    }
    return next(action);
  };
};

export default createMiddleware(Sentry);
