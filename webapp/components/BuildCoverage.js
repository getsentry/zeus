import React, {Component} from 'react';
import PropTypes from 'prop-types';

export default class BuildCoverage extends Component {
  static propTypes = {
    build: PropTypes.object.isRequired
  };

  getCoverage() {
    let {build} = this.props;
    if (build.status !== 'finished') return '';
    if (build.stats.coverage.diff_lines_covered === 0) return '0%';
    return `${parseInt(
      build.stats.coverage.diff_lines_covered /
        (build.stats.coverage.diff_lines_uncovered +
          build.stats.coverage.diff_lines_uncovered) *
        100,
      10
    )}%`;
  }

  render() {
    return (
      <span>
        {this.getCoverage()}
      </span>
    );
  }
}
