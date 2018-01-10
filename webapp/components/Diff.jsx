import React, {Component} from 'react';
import PropTypes from 'prop-types';
import SyntaxHighlight from './SyntaxHighlight';

export default class Diff extends Component {
  static propTypes = {
    diff: PropTypes.string.isRequired
  };

  render() {
    return <SyntaxHighlight lang="diff">{this.props.diff}</SyntaxHighlight>;
  }
}
