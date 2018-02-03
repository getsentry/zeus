import thunk from 'redux-thunk';
import {createStore, applyMiddleware, compose} from 'redux';

import reducers from './reducers';
import debugToolbar from './middleware/debugToolbar';
import stream from './middleware/stream';

export default createStore(
  reducers,
  compose(
    applyMiddleware(thunk, stream),
    applyMiddleware(thunk, debugToolbar),
    window.devToolsExtension ? window.devToolsExtension() : f => f
  )
);
