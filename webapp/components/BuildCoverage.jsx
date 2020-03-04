import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {Link} from 'react-router';
import styled from '@emotion/styled';

import Section from '../components/Section';
import {ResultGrid, Column, Header, Row} from '../components/ResultGrid';
import SyntaxHighlight from '../components/SyntaxHighlight';
import {Tree, Leaf, TreeWrapper, TreeSummary} from '../components/Tree';

const StyledResultGrid = styled(ResultGrid)``;

const StyledHeader = styled(Header)`
  border-color: #ccc;
`;

const StyledRow = styled(Row)`
  border-color: #ccc;
  padding: 0;

  &.good {
    background-color: #e2f5e7;
  }

  &.warn {
    background-color: #ffedde;
  }

  &.bad {
    background-color: #ffe9e9;
  }
`;

const StyledColumn = styled(Column)`
  padding: 8px 4px;
  border-left: 1px solid #ccc;

  &:last-child {
    border-right: 1px solid #ccc;
  }
`;

const FileWithCoverageTable = styled.table`
  width: 100%;

  a { color: inherit; }

  pre {
    margin-bottom: 0;
    padding: 0: !important;
    background: #fff !important;
    white-space: pre !important;
    overflow-wrap: normal !important;
    word-wrap: normal !important;
  }

  .line-c {
    background-color: #76d392 !important;
  }

  .line-u {
    background-color: #f05b5b !important;
  }

  .line-n {
    background-color: #eee !important;
  }

  td {
    vertical-align: top;
    font-size: 14px !important;
  }

  tr > td:first-of-type {
    width: 30px;
    text-align: right;
  }

  tr > td:nth-child(2) {
    width: 20px;
  }

  tr > td:nth-child(3) {
    white-space: nowrap;
    overflow: scroll;
  }
`;

class CoveredFile extends Component {
  static propTypes = {
    result: PropTypes.object.isRequired
  };

  render() {
    let {result} = this.props;
    if (!result.file_source) {
      return <p>We were unable to render the source for this file.</p>;
    }
    let lines = result.file_source.split('\n');
    return (
      <FileWithCoverageTable>
        <tr>
          <td>
            {lines.map((l, n) => {
              return (
                <div key={n}>
                  <a href={`#L${n + 1}`} id={`L${n + 1}`}>
                    <code key={n}>{n + 1}</code>
                  </a>
                </div>
              );
            })}
          </td>
          <td>
            {lines.map((l, n) => {
              let lineCov = result.coverage.data[n];
              return (
                <pre key={n} className={`line-${(lineCov || 'N').toLowerCase()}`}>
                  &nbsp;
                </pre>
              );
            })}
          </td>
          <td>
            <SyntaxHighlight filename={result.coverage.filename}>
              {result.file_source}
            </SyntaxHighlight>
          </td>
        </tr>
      </FileWithCoverageTable>
    );
  }
}

class CoveredTree extends Component {
  static propTypes = {
    result: PropTypes.object.isRequired,
    location: PropTypes.object.isRequired
  };

  render() {
    let path = this.props.location.pathname;
    let {result} = this.props;
    return (
      <StyledResultGrid>
        <StyledHeader>
          <Column />
          <Column width={250} textAlign="right">
            Diff
          </Column>
          <Column width={250} textAlign="right">
            Overall
          </Column>
        </StyledHeader>
        {result.entries.map(entry => {
          let totalLines = entry.lines_covered + entry.lines_uncovered;
          let diffTotalLines = entry.diff_lines_covered + entry.diff_lines_uncovered;
          let pctCovered = entry.lines_covered
            ? parseInt((entry.lines_covered / totalLines) * 100, 10)
            : 0;
          let diffPctCovered = diffTotalLines
            ? entry.diff_lines_covered
              ? parseInt((entry.diff_lines_covered / diffTotalLines) * 100, 10)
              : 0
            : null;
          let className;
          if (pctCovered >= 100) {
            className = 'good';
          } else if (pctCovered >= 80) {
            className = 'warn';
          } else {
            className = 'bad';
          }
          return (
            <StyledRow key={entry.path} className={className}>
              <StyledColumn>
                {entry.numTests === 1 ? (
                  <span>{entry.name}</span>
                ) : (
                  <Link to={{pathname: path, query: {parent: entry.path}}}>
                    {entry.name}
                  </Link>
                )}
              </StyledColumn>
              <StyledColumn width={120} textAlign="right">
                {diffPctCovered !== null ? `${diffPctCovered}%` : '\u00A0'}
              </StyledColumn>
              <StyledColumn width={120} textAlign="right">
                {`${entry.diff_lines_covered.toLocaleString()} / ${diffTotalLines}`}
              </StyledColumn>
              <StyledColumn
                width={120}
                textAlign="right">{`${pctCovered}%`}</StyledColumn>
              <StyledColumn width={120} textAlign="right">
                {`${entry.lines_covered.toLocaleString()} / ${totalLines}`}
              </StyledColumn>
            </StyledRow>
          );
        })}
      </StyledResultGrid>
    );
  }
}

export default class BuildCoverage extends Component {
  static contextTypes = {
    repo: PropTypes.object.isRequired
  };

  static propTypes = {
    location: PropTypes.object.isRequired,
    result: PropTypes.object.isRequired
  };

  render() {
    let {repo} = this.context;
    let {result} = this.props;
    let path = this.props.location.pathname;
    let linesCovered = 0,
      linesTotal = 0,
      diffLinesCovered = 0,
      diffLinesTotal = 0;
    result.entries.forEach(e => {
      linesCovered += e.lines_covered;
      linesTotal += e.lines_covered + e.lines_uncovered;
      diffLinesCovered += e.diff_lines_covered;
      diffLinesTotal += e.diff_lines_covered + e.diff_lines_uncovered;
    });
    let pctCovered = parseInt((linesCovered / linesTotal) * 100, 10);
    let diffPctCovered = diffLinesTotal
      ? parseInt((diffLinesCovered / diffLinesTotal) * 100, 10)
      : null;

    return (
      <Section>
        <TreeWrapper>
          {!!result.trail.length && (
            <Tree>
              {result.trail.map(crumb => {
                return (
                  <Leaf
                    to={{pathname: path, query: {parent: crumb.path}}}
                    key={crumb.path}>
                    {crumb.name}
                  </Leaf>
                );
              })}
            </Tree>
          )}
          <TreeSummary>
            {!!result.build && (
              <p>
                Data from{' '}
                <Link
                  to={`${repo.full_name}/builds/${result.build.number}`}>{`${repo.owner_name}/${repo.name}#${result.build.number}`}</Link>
              </p>
            )}
            <p>
              <strong>Diff:</strong>{' '}
              {diffPctCovered !== null
                ? `${diffPctCovered}% lines covered (${diffLinesCovered} / ${diffLinesTotal})`
                : 'n/a'}
            </p>
            <p>
              <strong>Overall:</strong>{' '}
              {`${pctCovered}% lines covered (${linesCovered} / ${linesTotal})`}
            </p>
          </TreeSummary>
        </TreeWrapper>
        {result.is_leaf ? (
          <CoveredFile result={result} {...this.props} />
        ) : (
          <CoveredTree result={result} {...this.props} />
        )}
      </Section>
    );
  }
}
