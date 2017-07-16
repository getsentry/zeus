import {combineReducers} from 'redux';

import auth from './auth';
import indicators from './indicators';
import repos from './repos';

export default combineReducers({
  auth,
  indicators,
  repos
});
