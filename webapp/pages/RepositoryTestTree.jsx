import React from 'react';
import PropTypes from 'prop-types';
import {Link} from 'react-router';

import AsyncPage from '../components/AsyncPage';
import Duration from '../components/Duration';
import {ResultGrid, Column, Header, Row} from '../components/ResultGrid';
import {Tree, Leaf, TreeWrapper, TreeSummary} from '../components/Tree';

export default class RepositoryTestTree extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  getEndpoints() {
    let {repo} = this.context;
    return [
      ['result', `/repos/${repo.full_name}/test-tree`, {query: this.props.location.query}]
    ];
  }

  renderBody() {
    let path = this.props.location.pathname;
    let {result} = this.state;
    let {repo} = this.context;
    let testsTotal = 0,
      testsDuration = 0;
    result.entries.forEach(e => {
      testsTotal += e.numTests;
      testsDuration += e.totalDuration;
    });
    let avgDuration = testsDuration / testsTotal;

    return (
      <div>
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
                <Link to={`${repo.full_name}/builds/${result.build.number}`}>{`${
                  repo.owner_name
                }/${repo.name}#${result.build.number}`}</Link>
              </p>
            )}
            <p>
              {' '}
              {testsTotal.toLocaleString()} tests running in{' '}
              <Duration ms={testsDuration} short={false} /> (avg:{' '}
              <Duration ms={avgDuration} short={false} />)
            </p>
          </TreeSummary>
        </TreeWrapper>
        <ResultGrid>
          <Header>
            <Column />
            <Column width={90}>Tests</Column>
            <Column width={90}>Duration</Column>
          </Header>
          {result.entries.map(entry => {
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
                <Column width={90}>{entry.numTests.toLocaleString()}</Column>
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
