import React, {Component} from 'react';

import './PageLoadingIndicator.css';

export default class PageLoadingIndicator extends Component {
  render() {
    let points = 16;
    return (
      <div className="loading-line">
        {[...Array(16)].map(i => {
          return (
            <span key={i} className="loading-bit" style={{width: `${100 / points}%`}} />
          );
        })}
      </div>
    );
  }
}
