import React from 'react';
import moment from 'moment';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import Duration from '../components/Duration';
import FileSize from '../components/FileSize';
import {ResultGrid, Column, Header, Row} from '../components/ResultGrid';

export default class RepositoryStats extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  getEndpoints() {
    let {repo} = this.context;
    let endpoint = `/repos/${repo.full_name}/stats`;
    let params = {resolution: '1w', points: 52};
    return [
      ['buildsDuration', endpoint, {query: {stat: 'builds.duration', ...params}}],
      ['buildsFailed', endpoint, {query: {stat: 'builds.failed', ...params}}],
      ['buildsPassed', endpoint, {query: {stat: 'builds.passed', ...params}}],
      ['buildsTotal', endpoint, {query: {stat: 'builds.total', ...params}}],
      [
        'bundleTotalAssetSize',
        endpoint,
        {query: {stat: 'bundle.total_asset_size', ...params}}
      ],
      [
        'styleViolationsCount',
        endpoint,
        {query: {stat: 'style_violations.count', ...params}}
      ],
      ['testsCount', endpoint, {query: {stat: 'tests.count', ...params}}],
      ['testsDuration', endpoint, {query: {stat: 'tests.duration', ...params}}],
      ['linesCovered', endpoint, {query: {stat: 'coverage.lines_covered', ...params}}],
      ['linesUncovered', endpoint, {query: {stat: 'coverage.lines_uncovered', ...params}}]
    ];
  }

  renderBody() {
    let {
      buildsDuration,
      buildsFailed,
      buildsPassed,
      buildsTotal,
      bundleTotalAssetSize,
      styleViolationsCount,
      linesCovered,
      linesUncovered,
      testsCount,
      testsDuration
    } = this.state;
    let groupedStats = {};
    testsCount.forEach(({time, value}) => (groupedStats[time] = {'tests.count': value}));
    testsDuration.forEach(
      ({time, value}) => (groupedStats[time]['tests.duration'] = value)
    );
    linesCovered.forEach(
      ({time, value}) => (groupedStats[time]['coverage.lines_covered'] = value)
    );
    linesUncovered.forEach(
      ({time, value}) => (groupedStats[time]['coverage.lines_uncovered'] = value)
    );
    buildsDuration.forEach(
      ({time, value}) => (groupedStats[time]['builds.duration'] = value)
    );
    buildsTotal.forEach(({time, value}) => (groupedStats[time]['builds.total'] = value));
    buildsFailed.forEach(
      ({time, value}) => (groupedStats[time]['builds.failed'] = value)
    );
    buildsPassed.forEach(
      ({time, value}) => (groupedStats[time]['builds.passed'] = value)
    );
    bundleTotalAssetSize.forEach(
      ({time, value}) => (groupedStats[time]['bundle.total_asset_size'] = value)
    );
    styleViolationsCount.forEach(
      ({time, value}) => (groupedStats[time]['style_violations.count'] = value)
    );
    return (
      <ResultGrid>
        <Header>
          <Column>Week Of</Column>
          <Column width={100} textAlign="right">
            Total<br />Builds
          </Column>
          <Column width={100} textAlign="right">
            Avg<br />Duration
          </Column>
          <Column width={100} textAlign="right">
            Pct<br />Green Builds
          </Column>
          <Column width={100} textAlign="right">
            Avg<br />Coverage
          </Column>
          <Column width={100} textAlign="right">
            Tests<br />per Build
          </Column>
          <Column width={100} textAlign="right">
            Avg<br />Test Duration
          </Column>
          <Column width={100} textAlign="right">
            Style<br />Violations
          </Column>
          <Column width={100} textAlign="right">
            Bundle<br />Size
          </Column>
        </Header>
        {testsCount.map(({time}) => {
          let stat = groupedStats[time];
          let totalLines =
            stat['coverage.lines_covered'] + stat['coverage.lines_uncovered'];
          return (
            <Row key={time}>
              <Column>{moment(time).format('ll')}</Column>
              <Column width={100} textAlign="right">
                {stat['builds.total'].toLocaleString()}
              </Column>
              <Column width={100} textAlign="right">
                {stat['builds.duration'] ? <Duration ms={stat['builds.duration']} /> : ''}
              </Column>
              <Column width={100} textAlign="right">
                {stat['builds.total']
                  ? `${parseInt(
                      (stat['builds.passed'] || 0) / stat['builds.total'] * 1000,
                      10
                    ) / 10}%`
                  : ''}
              </Column>
              <Column width={100} textAlign="right">
                {totalLines
                  ? `${parseInt(stat['coverage.lines_covered'] / totalLines * 1000, 10) /
                      10}%`
                  : ''}
              </Column>
              <Column width={100} textAlign="right">
                {stat['tests.count'].toLocaleString()}
              </Column>
              <Column width={100} textAlign="right">
                {stat['tests.duration'] ? (
                  <Duration ms={stat['tests.duration'] / stat['tests.count']} />
                ) : (
                  ''
                )}
              </Column>
              <Column width={100} textAlign="right">
                {stat['style_violations.count'].toLocaleString()}
              </Column>
              <Column width={100} textAlign="right">
                <FileSize value={stat['bundle.total_asset_size']} />
              </Column>
            </Row>
          );
        })}
      </ResultGrid>
    );
  }
}
