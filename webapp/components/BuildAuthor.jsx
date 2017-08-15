import React, {Component} from 'react';
import PropTypes from 'prop-types';

export default class BuildCoverage extends Component {
  static propTypes = {
    build: PropTypes.object.isRequired
  };

  render() {
    let {build} = this.props;
    if (!build.source.author) return null;
    return (
      <span>
        {build.source.author.email || build.source.author.name}
      </span>
    );
  }
}
