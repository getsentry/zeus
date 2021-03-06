import React, {Component} from 'react';
import {Link} from 'react-router';
import PropTypes from 'prop-types';

import Collapsable from './Collapsable';
import {ResultGrid, Column, Header, Row} from './ResultGrid';

export default class CoverageSummary extends Component {
  static propTypes = {
    build: PropTypes.object,
    coverage: PropTypes.arrayOf(PropTypes.object).isRequired,
    collapsable: PropTypes.bool,
    repo: PropTypes.object.isRequired,
    maxVisible: PropTypes.number
  };

  static defaultProps = {
    collapsable: false
  };

  static contextTypes = {
    router: PropTypes.object.isRequired
  };

  constructor(props, context) {
    super(props, context);
    this.state = {collapsable: props.collapsable};
  }

  render() {
    let {build, coverage, repo} = this.props;
    // XXX(dcramer): dirty hack to ensure URL generation still works
    let link = build
      ? build.number
        ? `/${repo.full_name}/builds/${build.number}/coverage`
        : build.revision
        ? `/${repo.full_name}/revisions/${build.revision.sha}/coverage`
        : this.context.router.location.pathname
      : this.context.router.location.pathname;

    return (
      <ResultGrid>
        <Header>
          <Column>File</Column>
          <Column width={80} textAlign="right">
            Diff
          </Column>
          <Column width={80} textAlign="right">
            Overall
          </Column>
        </Header>
        <Collapsable
          collapsable={this.props.collapsable}
          maxVisible={this.props.maxVisible}>
          {coverage.map(fileCoverage => {
            let totalDiffLines =
              fileCoverage.diff_lines_covered + fileCoverage.diff_lines_uncovered;
            let totalLines = fileCoverage.lines_covered + fileCoverage.lines_uncovered;

            return (
              <Row key={fileCoverage.filename}>
                <Column>
                  <Link to={{pathname: link, query: {parent: fileCoverage.filename}}}>
                    {fileCoverage.filename}
                  </Link>
                </Column>
                <Column width={80} textAlign="right">
                  {totalDiffLines
                    ? `${parseInt(
                        (fileCoverage.diff_lines_covered / totalDiffLines) * 1000,
                        10
                      ) / 10}%`
                    : ''}
                </Column>
                <Column width={80} textAlign="right">
                  {totalLines
                    ? `${parseInt((fileCoverage.lines_covered / totalLines) * 1000, 10) /
                        10}%`
                    : ''}
                </Column>
              </Row>
            );
          })}
        </Collapsable>
      </ResultGrid>
    );
  }
}
