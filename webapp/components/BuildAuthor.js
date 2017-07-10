import React, {Component} from 'react';
import PropTypes from 'prop-types';

export default class BuildCoverage extends Component {
  static propTypes = {
    build: PropTypes.object.isRequired
  };

  render() {
    let {build} = this.props;
    return (
      <span>
        {build.author ? build.author.name : <em>anonymous</em>}
      </span>
    );
  }
}
