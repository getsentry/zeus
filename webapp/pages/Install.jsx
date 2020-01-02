import React from 'react';
import moment from 'moment';
import {Flex, Box} from '@rebass/grid/emotion';
import styled from '@emotion/styled';

import AsyncPage from '../components/AsyncPage';
import Layout from '../components/Layout';
import {Column, Header, ResultGrid, Row} from '../components/ResultGrid';
import requireAuth from '../utils/requireAuth';
import Section from '../components/Section';
import SectionHeading from '../components/SectionHeading';

const StatPanel = styled(Section)`
  border: 3px solid #eee;
  font-size: 20px;
  padding: 20px;
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow: hidden;
`;

class InstallStatsTable extends AsyncPage {
  getEndpoints() {
    let endpoint = `/install/stats`;
    let params = {resolution: '1w', points: 52};
    return [
      ['buildsErrored', endpoint, {query: {stat: 'builds.errored', ...params}}],
      ['buildsTotal', endpoint, {query: {stat: 'builds.total', ...params}}],
      ['usersCreated', endpoint, {query: {stat: 'users.created', ...params}}]
    ];
  }

  renderBody() {
    let {buildsErrored, buildsTotal, usersCreated} = this.state;
    let groupedStats = {};
    buildsTotal.forEach(
      ({time, value}) => (groupedStats[time] = {'builds.total': value})
    );
    buildsErrored.forEach(
      ({time, value}) => (groupedStats[time]['builds.errored'] = value)
    );
    usersCreated.forEach(
      ({time, value}) => (groupedStats[time]['users.created'] = value)
    );
    return (
      <ResultGrid>
        <Header>
          <Column>Week Of</Column>
          <Column width={100} textAlign="right">
            Total
            <br />
            Builds
          </Column>
          <Column width={100} textAlign="right">
            Build
            <br />
            Errors
          </Column>
          <Column width={100} textAlign="right">
            Created
            <br />
            Users
          </Column>
        </Header>
        {buildsTotal.map(({time}) => {
          let stat = groupedStats[time];
          return (
            <Row key={time}>
              <Column>{moment(time).format('ll')}</Column>
              <Column width={100} textAlign="right">
                {stat['builds.total'].toLocaleString()}
              </Column>
              <Column width={100} textAlign="right">
                {stat['builds.errored'].toLocaleString()}
              </Column>
              <Column width={100} textAlign="right">
                {stat['users.created'].toLocaleString()}
              </Column>
            </Row>
          );
        })}
      </ResultGrid>
    );
  }
}

class InstallStatsHeader extends AsyncPage {
  getEndpoints() {
    return [['data', '/install']];
  }

  renderBody() {
    let {
      data: {stats, config}
    } = this.state;
    return (
      <Flex flex="1">
        <Box width={3 / 12} mr={4}>
          <StatPanel>
            <SectionHeading>
              Users Active <small>30d</small>
            </SectionHeading>
            {stats.users.active['30d'].toLocaleString()}
          </StatPanel>
        </Box>
        <Box width={3 / 12} mr={4}>
          <StatPanel>
            <SectionHeading>
              Repos Active <small>30d</small>
            </SectionHeading>
            {stats.repos.active['30d'].toLocaleString()}
          </StatPanel>
        </Box>
        <Box width={3 / 12} mr={4}>
          <StatPanel>
            <SectionHeading>
              Jobs Created <small>30d</small>
            </SectionHeading>
            {stats.jobs.created['30d'].toLocaleString()}
          </StatPanel>
        </Box>
        <Box width={3 / 12}>
          <StatPanel>
            <SectionHeading>
              API Version <small>{config.environment}</small>
            </SectionHeading>
            <a href={`https://github.com/getsentry/zeus/commit/${config.release}`}>
              {config.release}
            </a>
          </StatPanel>
        </Box>
      </Flex>
    );
  }
}

class Install extends AsyncPage {
  getTitle() {
    return 'Zeus Install';
  }

  renderBody() {
    return (
      <Layout>
        <h1>Installation Overview</h1>
        <InstallStatsHeader />
        <InstallStatsTable />
      </Layout>
    );
  }
}

export default requireAuth(Install);
