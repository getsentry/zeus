import React, {Component} from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import {Flex, Box} from 'grid-styled';

import BuildListItem from '../components/BuildListItem';
import Panel from '../components/Panel';

export default class BuildList extends Component {
  static propTypes = {
    buildList: PropTypes.arrayOf(PropTypes.object).isRequired
  };

  render() {
    return (
      <Panel>
        <BuildListHeader>
          <Flex>
            <Box flex="1" width={6 / 12} pr={15}>
              Build
            </Box>
            <Box width={1 / 12} style={{textAlign: 'center'}}>
              Duration
            </Box>
            <Box width={1 / 12} style={{textAlign: 'center'}}>
              Coverage
            </Box>
            <Box width={2 / 12}>Author</Box>
            <Box width={2 / 12} style={{textAlign: 'right'}}>
              When
            </Box>
          </Flex>
        </BuildListHeader>
        <div>
          {this.props.buildList.map(build => {
            return (
              <BuildListItem key={build.id} build={build} params={this.props.params} />
            );
          })}
        </div>
      </Panel>
    );
  }
}

const BuildListHeader = styled.div`
  padding: 10px 15px;
  border-bottom: 1px solid #dbdae3;
  font-size: 13px;
  color: #767488;
  font-weight: 500;
  text-transform: uppercase;
`;
