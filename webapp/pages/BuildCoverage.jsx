import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {Link} from 'react-router';
import styled from 'styled-components';
import SyntaxHighlighter from 'react-syntax-highlighter';

import AsyncPage from '../components/AsyncPage';
import Section from '../components/Section';
import {ResultGrid, Column, Header, Row} from '../components/ResultGrid';

const Tree = styled.div`
  margin-bottom: 20px;
`;

const Leaf = styled(Link)`
  color: #000;
  font-weight: 400;

  &:after {
    margin: 0 5px;
    content: ' / ';
    color: #ddd;
  }

  &:last-child {
    color: #666;
    &:after {
      display: none;
    }
  }
`;

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

  pre {
    margin-bottom: 0;
    padding: 0: !important;
    background: #fff !important;
  }

  .line-c {
    background-color: #76d392 !important;
  }

  .line-u {
    background-color: #ffe9e9 !important;
  }

  td {
    vertical-align: top;
    font-size: 14px !important;
  }

  tr > td:first-child {
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

const CoveredSummary = styled(Section)`
  border: 2px solid #eee;
  padding: 10px;
`;

const CoveredStats = styled.div`
  font-size: 0.8em;
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
              return <pre key={n}>{n + 1}</pre>;
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
            <SyntaxHighlighter style={{padding: 0}}>
              {result.file_source}
            </SyntaxHighlighter>
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
          <Column width={180} textAlign="right">
            Lines
          </Column>
        </StyledHeader>
        {result.entries.map(entry => {
          let totalLines = entry.lines_covered + entry.lines_uncovered;
          let pctCovered = parseInt(entry.lines_covered / totalLines * 100, 10);
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
              <StyledColumn width={90} textAlign="right">{`${pctCovered}%`}</StyledColumn>
              <StyledColumn width={90} textAlign="right">
                {`${entry.lines_covered.toLocaleString()} / ${totalLines}`}
              </StyledColumn>
            </StyledRow>
          );
        })}
      </StyledResultGrid>
    );
  }
}

export default class BuildCoverageTree extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    build: PropTypes.object.isRequired,
    repo: PropTypes.object.isRequired
  };

  getEndpoints() {
    let {repo} = this.context;
    let {buildNumber} = this.props.params;
    return [
      [
        'result',
        `/repos/${repo.full_name}/builds/${buildNumber}/file-coverage-tree`,
        {query: this.props.location.query}
      ]
    ];
  }

  renderBody() {
    let {result} = this.state;
    let path = this.props.location.pathname;
    let linesCovered = 0,
      linesTotal = 0;
    result.entries.forEach(e => {
      linesCovered += e.lines_covered;
      linesTotal += e.lines_covered + e.lines_uncovered;
    });
    let pctCovered = parseInt(linesCovered / linesTotal * 100, 10);

    return (
      <Section>
        <CoveredSummary>
          <Tree>
            {result.trail.map(crumb => {
              return (
                <Leaf to={{pathname: path, query: {parent: crumb.path}}} key={crumb.path}>
                  {crumb.name}
                </Leaf>
              );
            })}
          </Tree>{' '}
          <CoveredStats>{`${pctCovered}% lines covered (${linesCovered} / ${linesTotal})`}</CoveredStats>
        </CoveredSummary>
        {result.is_leaf ? (
          <CoveredFile result={result} {...this.props} />
        ) : (
          <CoveredTree result={result} {...this.props} />
        )}
      </Section>
    );
  }
}
