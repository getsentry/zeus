import React from 'react';
import PropTypes from 'prop-types';
import {Link} from 'react-router';
import styled from 'styled-components';

import AsyncPage from '../components/AsyncPage';
import Section from '../components/Section';
import {ResultGrid, Column, Header, Row} from '../components/ResultGrid';

const Tree = styled.div`
  margin-bottom: 20px;
`;

const Leaf = styled(Link)`
  color: #000;

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
        'tree',
        `/repos/${repo.full_name}/builds/${buildNumber}/file-coverage-tree`,
        {query: this.props.location.query}
      ]
    ];
  }

  renderBody() {
    let path = this.props.location.pathname;
    return (
      <Section>
        <Tree>
          {this.state.tree.trail.map(crumb => {
            return (
              <Leaf to={{pathname: path, query: {parent: crumb.path}}} key={crumb.path}>
                {crumb.name}
              </Leaf>
            );
          })}
        </Tree>
        <ResultGrid>
          <Header>
            <Column />
            <Column width={90}>Lines</Column>
            <Column width={90} />
          </Header>
          {this.state.tree.entries.map(entry => {
            let totalLines = entry.lines_covered + entry.lines_uncovered;
            let pctCovered = parseInt(entry.lines_covered / totalLines * 100, 10);
            return (
              <Row key={entry.path}>
                <Column>
                  {entry.numTests === 1 ? (
                    <span>{entry.name}</span>
                  ) : (
                    <Link to={{pathname: path, query: {parent: entry.path}}}>
                      {entry.name}
                    </Link>
                  )}
                </Column>
                <Column width={90}>{`${pctCovered}%`}</Column>
                <Column width={90}>
                  {`${entry.lines_covered.toLocaleString()} / ${totalLines}`}
                </Column>
              </Row>
            );
          })}
        </ResultGrid>
      </Section>
    );
  }
}
