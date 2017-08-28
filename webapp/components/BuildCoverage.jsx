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
    let totalDiffLines =
      build.stats.coverage.diff_lines_uncovered +
      build.stats.coverage.diff_lines_uncovered;
    if (!totalDiffLines) return '';
    return `${parseInt(
      build.stats.coverage.diff_lines_covered / totalDiffLines * 100,
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
