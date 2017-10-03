import React from 'react';
import PropTypes from 'prop-types';
import {Link} from 'react-router';
import {Flex, Box} from 'grid-styled';
import styled from 'styled-components';

import AsyncPage from '../components/AsyncPage';
import Duration from '../components/Duration';
import ResultGridHeader from '../components/ResultGridHeader';
import ResultGridRow from '../components/ResultGridRow';

const Tree = styled.div``;

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
        <ResultGridHeader>
          <Flex align="center">
            <Box flex="1" width={11 / 12} pr={15} />
            <Box width={1 / 12} style={{textAlign: 'right'}}>
              Tests
            </Box>
            <Box width={1 / 12} style={{textAlign: 'right'}}>
              Duration
            </Box>
          </Flex>
        </ResultGridHeader>
        {this.state.tree.entries.map(entry => {
          return (
            <ResultGridRow key={entry.path}>
              <Flex align="center">
                <Box flex="1" width={11 / 12} pr={15}>
                  {entry.numTests === 1
                    ? <span>
                        {entry.name}
                      </span>
                    : <Link to={{pathname: path, query: {parent: entry.path}}}>
                        {entry.name}
                      </Link>}
                </Box>
                <Box width={1 / 12} style={{textAlign: 'right'}}>
                  {entry.numTests.toLocaleString()}
                </Box>
                <Box width={1 / 12} style={{textAlign: 'right'}}>
                  <Duration ms={entry.totalDuration} />
                </Box>
              </Flex>
            </ResultGridRow>
          );
        })}
      </div>
    );
  }
}
