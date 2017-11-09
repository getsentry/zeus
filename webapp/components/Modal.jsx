import React, {Component} from 'react';
import PropTypes from 'prop-types';

import Logo from '../assets/Logo';

export default class CalloutBox extends Component {
  static propTypes = {
    title: PropTypes.string.isRequired,
    subtext: PropTypes.string
  };

  render() {
    return (
      <div style={{margin: 'auto', maxWidth: 800}}>
        <div
          style={{
            border: '10px solid #111',
            margin: 20,
            borderRadius: '4px',
            padding: 20
          }}>
          {this.props.subtext
            ? <h1 style={{opacity: 0.2, float: 'right'}}>
                {this.props.subtext}
              </h1>
            : null}
          <h1>
            {this.props.title}
          </h1>
          {this.props.children}
        </div>
        <div style={{textAlign: 'center'}}>
          <a href="/">
            <Logo size="30" />
          </a>
        </div>
      </div>
    );
  }
}
