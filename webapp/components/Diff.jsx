import React, {Component} from 'react';
import PropTypes from 'prop-types';
import Highlight from 'react-hljs';

import './Diff.css';

export default class Diff extends Component {
  static propTypes = {
    diff: PropTypes.string.isRequired
  };

  render() {
    return (
      <Highlight className="diff">
        {this.props.diff}
      </Highlight>
    );
  }
}
