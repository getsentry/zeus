import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {Flex, Box} from 'grid-styled';
import styled from 'styled-components';

import {Client} from '../api';

import Collapsable from './Collapsable';
import ObjectDuration from './ObjectDuration';
import ObjectResult from './ObjectResult';
import Panel from './Panel';
import ResultGridRow from './ResultGridRow';

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
    let {buildNumber, ownerName, repoName} = this.props.params;
    this.api
      .request(`/repos/${ownerName}/${repoName}/builds/${buildNumber}/tests/${test.name}`)
      .then(testDetails => {
        this.setState({loading: false, testDetails});
      });
  }

  componentWillUnmount() {
    this.api.clear();
  }

  render() {
    if (this.state.loading) return <TestDetailsWrapper>(loading)</TestDetailsWrapper>;
    let {testDetails} = this.state;
    return (
      <TestDetailsWrapper>
        <pre style={{margin: 0}}>
          {testDetails.message || <em>no output captured</em>}
        </pre>
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
            <Box flex="1" width={11 / 12} pr={15}>
              <ObjectResult data={test} />
              {test.name}
            </Box>
            <Box width={1 / 12} style={{textAlign: 'right'}}>
              <ObjectDuration data={test} short={true} />
            </Box>
          </Flex>
          {this.state.expanded && <TestDetails test={test} params={params} />}
        </ResultGridRow>
      </TestListItemLink>
    );
  }
}

export default class TestList extends Component {
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
      <Panel>
        <Collapsable
          collapsable={this.props.collapsable}
          maxVisible={this.props.maxVisible}>
          {this.props.testList.map(test => {
            return (
              <TestListItem params={this.props.params} test={test} key={test.name} />
            );
          })}
        </Collapsable>
      </Panel>
    );
  }
}

const TestDetailsWrapper = styled.div`
  margin-top: 10px;
  padding: 10px 0 0 25px;
  color: #39364e;
  font-size: 12px;
  border-top: 1px solid #dbdae3;
`;

const TestListItemLink = styled.a`
  display: block;
  cursor: pointer;

  &:hover {
    background-color: #f0eff5;
  }
`;
