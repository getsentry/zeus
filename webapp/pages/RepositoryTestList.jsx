import React, {Component} from 'react';
import {Link} from 'react-router';
import PropTypes from 'prop-types';
import {Flex, Box} from '@rebass/grid/emotion';
import styled from '@emotion/styled';

import AsyncPage from '../components/AsyncPage';
import Paginator from '../components/Paginator';
import Section from '../components/Section';

import Duration from '../components/Duration';
import ResultGridRow from '../components/ResultGridRow';
import {ResultGrid, Column, Header} from '../components/ResultGrid';

class TestListItem extends Component {
  static propTypes = {
    repo: PropTypes.object.isRequired,
    test: PropTypes.object.isRequired
  };

  render() {
    let {repo, test} = this.props;
    return (
      <TestListItemLink to={`/${repo.full_name}/reports/tests/${test.hash}`}>
        <ResultGridRow>
          <Flex align="center">
            <Box flex="1">{test.name}</Box>
            <Box width={120} style={{textAlign: 'right'}}>
              {test.runs_failed.toLocaleString()}
            </Box>
            <Box width={120} style={{textAlign: 'right'}}>
              {parseInt((1 - test.runs_failed / test.runs_total) * 100, 10)}%
            </Box>
            <Box width={120} style={{textAlign: 'right'}}>
              {test.runs_total.toLocaleString()}
            </Box>
            <Box width={120} style={{textAlign: 'right'}}>
              <Duration ms={test.avg_duration} short={true} />
            </Box>
          </Flex>
        </ResultGridRow>
      </TestListItemLink>
    );
  }
}

class TestList extends Component {
  render() {
    return (
      <ResultGrid>
        <Header>
          <Column>Test Case</Column>
          <Column width={120} textAlign="right">
            Failed Runs
          </Column>
          <Column width={120} textAlign="right">
            Pass Rate
          </Column>
          <Column width={120} textAlign="right">
            Total Runs
          </Column>
          <Column width={120} textAlign="right">
            Avg Duration
          </Column>
        </Header>
        {this.props.testList.map(test => {
          return <TestListItem repo={this.props.repo} test={test} key={test.name} />;
        })}
      </ResultGrid>
    );
  }
}

const TestListItemLink = styled(Link)`
  display: block;
  cursor: pointer;

  &:hover {
    background-color: #f0eff5;
  }
`;

export default class RepositoryTestList extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  getEndpoints() {
    let {repo} = this.context;
    return [['testList', `/repos/${repo.full_name}/tests`]];
  }

  renderBody() {
    return (
      <Section>
        <TestList repo={this.context.repo} testList={this.state.testList} />
        <Paginator links={this.state.testList.links} {...this.props} />
      </Section>
    );
  }
}
