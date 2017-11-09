import React, {Component} from 'react';
import PropTypes from 'prop-types';
import SyntaxHighlighter from 'react-syntax-highlighter';

import './Diff.css';

export default class Diff extends Component {
  static propTypes = {
    diff: PropTypes.string.isRequired
  };

  render() {
    return (
      <SyntaxHighlighter language="diff" className="diff">
        {this.props.diff}
      </SyntaxHighlighter>
    );
  }
}
