import thunk from 'redux-thunk';
import {createStore, applyMiddleware, compose} from 'redux';

import reducers from './reducers';
import stream from './middleware/stream';

export default createStore(
  reducers,
  compose(
    applyMiddleware(thunk, stream),
    window.devToolsExtension ? window.devToolsExtension() : f => f
  )
);
