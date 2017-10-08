import React, {Component} from 'react';
import PropTypes from 'prop-types';

export default class BuildCoverage extends Component {
  static propTypes = {
    data: PropTypes.object.isRequired
  };

  getCoverage() {
    let {data} = this.props;
    if (data.status !== 'finished') return '';
    if (!data.stats.coverage) return '';
    let totalDiffLines =
      data.stats.coverage.diff_lines_uncovered + data.stats.coverage.diff_lines_covered;
    if (totalDiffLines === 0) return '';
    if (data.stats.coverage.diff_lines_covered === 0) return '0%';
    return `${parseInt(
      data.stats.coverage.diff_lines_covered / totalDiffLines * 100,
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
