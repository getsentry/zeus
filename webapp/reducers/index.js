import {combineReducers} from 'redux';

import auth from './auth';
import indicators from './indicators';

export default combineReducers({
  auth,
  indicators
});
