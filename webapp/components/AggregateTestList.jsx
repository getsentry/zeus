import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {Flex, Box} from 'grid-styled';
import {Link} from 'react-router';
import styled from 'styled-components';
import ExpandIcon from 'react-icons/lib/md/expand-more';
import CollapseIcon from 'react-icons/lib/md/expand-less';

import {Client} from '../api';

import Collapsable from './Collapsable';
import {AggregateDuration} from './ObjectDuration';
import ObjectResult from './ObjectResult';
import ResultGridRow from './ResultGridRow';
import {ResultGrid, Column, Header} from './ResultGrid';

class TestDetails extends Component {
  static propTypes = {
    test: PropTypes.object.isRequired,
    build: PropTypes.object.isRequired
  };

  constructor(props, context) {
    super(props, context);
    this.state = {loading: true};
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
    let {build} = this.props;
    if (this.state.loading) return <TestDetailsWrapper>(loading)</TestDetailsWrapper>;
    let {testDetails} = this.state;
    return (
      <TestDetailsWrapper>
        <h5>
          <ObjectResult data={testDetails} size={12} />#{build.number}.
          {testDetails.job.number}
          {testDetails.job.label && ` - ${testDetails.job.label}`}
        </h5>
        <pre>{testDetails.message || <em>no output captured</em>}</pre>
      </TestDetailsWrapper>
    );
  }
}

class TestListItem extends Component {
  static propTypes = {
    test: PropTypes.object.isRequired,
    build: PropTypes.object.isRequired,
    repo: PropTypes.object.isRequired,
    params: PropTypes.object
  };

  constructor(props, context) {
    super(props, context);
    this.state = {expanded: false};
  }

  render() {
    let {build, params, repo, test} = this.props;
    let {origin_build} = test;
    return (
      <ResultGridRow>
        <Flex align="center">
          <Box flex="1">
            <ObjectResult data={test} />
            <TestLink
              onClick={() => {
                window.getSelection().toString().length === 0 &&
                  this.setState({expanded: !this.state.expanded});
              }}>
              {test.name}
              <span className="toggle">
                {this.state.expanded ? (
                  <CollapseIcon size={12} />
                ) : (
                  <ExpandIcon size={12} />
                )}
              </span>
            </TestLink>
            {!!origin_build && (
              <OriginBuild>
                {' '}
                Originated in{' '}
                <Link to={`/${repo.full_name}/builds/${origin_build.number}`}>
                  #{origin_build.number}
                </Link>
              </OriginBuild>
            )}
          </Box>
          <Box width={90} style={{textAlign: 'right'}}>
            <AggregateDuration data={test.runs} />
          </Box>
        </Flex>
        {this.state.expanded && (
          <div>
            {test.runs.map(run => (
              <TestDetails build={build} test={run} params={params} key={run.id} />
            ))}
          </div>
        )}
      </ResultGridRow>
    );
  }
}

export default class AggregateTestList extends Component {
  static propTypes = {
    build: PropTypes.object.isRequired,
    repo: PropTypes.object.isRequired,
    testList: PropTypes.arrayOf(PropTypes.object).isRequired,
    collapsable: PropTypes.bool,
    maxVisible: PropTypes.number,
    params: PropTypes.object
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
              <TestListItem
                build={this.props.build}
                repo={this.props.repo}
                params={this.props.params}
                test={test}
                key={test.name}
              />
            );
          })}
        </Collapsable>
      </ResultGrid>
    );
  }
}

const TestDetailsWrapper = styled.div`
  margin-top: 10px;
  padding: 5px 0 0 25px;
  color: #39364e;
  font-size: 12px;
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
    font-size: 13px;
  }
`;

const TestLink = styled.a`
  display: inline-block;
  cursor: pointer;

  .toggle {
    margin-left: 5px;
    visibility: hidden;
  }

  &:hover .toggle {
    visibility: visible;
  }
`;

const OriginBuild = styled.span`
  display: inline-block;
  margin-left: 10px;
  font-size: 12px;
  background: #eee;
  padding: 1px 5px;
`;
