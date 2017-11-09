import React from 'react';
import PropTypes from 'prop-types';
import {Link} from 'react-router';
import styled from 'styled-components';

import AsyncPage from '../components/AsyncPage';
import Duration from '../components/Duration';
import {ResultGrid, Column, Header, Row} from '../components/ResultGrid';

const Tree = styled.div`margin-bottom: 20px;`;

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

export default class RepositoryTestTree extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  getEndpoints() {
    let {repo} = this.context;
    return [
      ['tree', `/repos/${repo.full_name}/test-tree`, {query: this.props.location.query}]
    ];
  }

  renderBody() {
    let path = this.props.location.pathname;
    return (
      <div>
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
            <Column width={90}>Tests</Column>
            <Column width={90}>Duration</Column>
          </Header>
          {this.state.tree.entries.map(entry => {
            return (
              <Row key={entry.path}>
                <Column>
                  {entry.numTests === 1
                    ? <span>
                        {entry.name}
                      </span>
                    : <Link to={{pathname: path, query: {parent: entry.path}}}>
                        {entry.name}
                      </Link>}
                </Column>
                <Column width={90}>
                  {entry.numTests.toLocaleString()}
                </Column>
                <Column width={90}>
                  <Duration ms={entry.totalDuration} />
                </Column>
              </Row>
            );
          })}
        </ResultGrid>
      </div>
    );
  }
}
