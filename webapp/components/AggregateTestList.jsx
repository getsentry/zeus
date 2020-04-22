import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {Flex, Box} from '@rebass/grid/emotion';
import {Link} from 'react-router';
import styled from '@emotion/styled';
import {MdExpandLess, MdExpandMore, MdHistory} from 'react-icons/md';

import Collapsable from './Collapsable';
import {AggregateDuration} from './ObjectDuration';
import Icon from './Icon';
import ObjectResult from './ObjectResult';
import ResultGridRow from './ResultGridRow';
import {ResultGrid, Column, Header} from './ResultGrid';
import TestDetails from './TestDetails';

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
                  <Icon>
                    <MdExpandLess size={12} />
                  </Icon>
                ) : (
                  <Icon>
                    <MdExpandMore size={12} />
                  </Icon>
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
          <Box width={40} style={{textAlign: 'right'}}>
            <Link to={`/${repo.full_name}/reports/tests/${test.hash}`}>
              <Icon>
                <MdHistory size={20} />
              </Icon>
            </Link>
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
          <Column width={40} textAlign="right" />
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
