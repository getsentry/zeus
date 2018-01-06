import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {Flex, Box} from 'grid-styled';
import styled from 'styled-components';

import {Client} from '../api';

import Collapsable from './Collapsable';
import {AggregateDuration} from './ObjectDuration';
import ObjectResult from './ObjectResult';
import ResultGridRow from './ResultGridRow';
import {ResultGrid, Column, Header} from './ResultGrid';

class TestDetails extends Component {
  static propTypes = {
    test: PropTypes.object.isRequired
  };

  constructor(props, context) {
    super(props, context);
    this.state = {loading: true};
  }

  componentWillMount() {
    this.api = new Client();
  }

  componentDidMount() {
    let {test} = this.props;
    this.api.request(`/tests/${test.id}`).then(testDetails => {
      this.setState({loading: false, testDetails});
    });
  }

  componentWillUnmount() {
    this.api.clear();
  }

  // TODO(dcramer): make this more useful
  render() {
    if (this.state.loading) return <TestDetailsWrapper>(loading)</TestDetailsWrapper>;
    let {testDetails} = this.state;
    return (
      <TestDetailsWrapper>
        <h5>
          <ObjectResult data={testDetails} size={12} /> Job #{testDetails.job.number}
          {testDetails.job.label && <span> &mdash; {testDetails.job.label}</span>}
        </h5>
        <pre>{testDetails.message || <em>no output captured</em>}</pre>
      </TestDetailsWrapper>
    );
  }
}

class TestListItem extends Component {
  static propTypes = {
    test: PropTypes.object.isRequired
  };

  constructor(props, context) {
    super(props, context);
    this.state = {expanded: false};
  }

  render() {
    let {params, test} = this.props;
    return (
      <TestListItemLink onClick={() => this.setState({expanded: !this.state.expanded})}>
        <ResultGridRow>
          <Flex align="center">
            <Box flex="1">
              <ObjectResult data={test} />
              {test.name}
            </Box>
            <Box width={90} style={{textAlign: 'right'}}>
              <AggregateDuration data={test.runs} />
            </Box>
          </Flex>
          {this.state.expanded && (
            <div>
              {test.runs.map(run => (
                <TestDetails test={run} params={params} key={run.id} />
              ))}
            </div>
          )}
        </ResultGridRow>
      </TestListItemLink>
    );
  }
}

export default class AggregateTestList extends Component {
  static propTypes = {
    testList: PropTypes.arrayOf(PropTypes.object).isRequired,
    collapsable: PropTypes.bool,
    maxVisible: PropTypes.number
  };

  static defaultProps = {
    collapsable: false
  };

  render() {
    return (
      <ResultGrid>
        <Header>
          <Column>Test Case</Column>
          <Column width={90} textAlign="right">
            Duration
          </Column>
        </Header>
        <Collapsable
          collapsable={this.props.collapsable}
          maxVisible={this.props.maxVisible}>
          {this.props.testList.map(test => {
            return (
              <TestListItem params={this.props.params} test={test} key={test.name} />
            );
          })}
        </Collapsable>
      </ResultGrid>
    );
  }
}

const TestDetailsWrapper = styled.div`
  margin-top: 10px;
  padding: 10px 0 0 25px;
  color: #39364e;
  font-size: 13px;
  line-height: 1.4em;
  border-top: 1px solid #eee;

  pre {
    font-size: inherit;
    margin: 0;
    background: #f9f9f9;
    padding: 5px;
    border-radius: 4px;
  }

  h5 {
    margin-bottom: 5px;
  }
`;

const TestListItemLink = styled.a`
  display: block;
  cursor: pointer;

  &:hover {
    background-color: #f0eff5;
  }
`;
