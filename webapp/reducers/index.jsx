import {combineReducers} from 'redux';

import auth from './auth';
import builds from './builds';
import indicators from './indicators';
import repos from './repos';
import revisions from './revisions';
import stream from './stream';

export default combineReducers({
  auth,
  builds,
  indicators,
  repos,
  revisions,
  stream
});
