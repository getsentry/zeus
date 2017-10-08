import React, {Component} from 'react';
import PropTypes from 'prop-types';

export default class ObjectCoverage extends Component {
  static propTypes = {
    data: PropTypes.object.isRequired,
    diff: PropTypes.object
  };

  static defaultProps = {
    diff: true
  };

  getCoverage() {
    let {data, diff} = this.props;
    if (data.status !== 'finished') return '';
    if (!data.stats.coverage) return '';
    let covStats = data.stats.coverage;
    let linesCovered = diff ? covStats.diff_lines_covered : covStats.lines_uncovered,
      linesUncovered = diff ? covStats.diff_lines_uncovered : covStats.lines_uncovered;
    let totalLines = linesCovered + linesUncovered;
    if (totalLines === 0) return '';
    if (linesCovered === 0) return '0%';
    return `${parseInt(linesCovered / totalLines * 100, 10)}%`;
  }

  render() {
    return (
      <span>
        {this.getCoverage()}
      </span>
    );
  }
}
