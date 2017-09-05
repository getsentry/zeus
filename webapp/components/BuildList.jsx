import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {Flex, Box} from 'grid-styled';

import BuildListItem from '../components/BuildListItem';
import Panel from '../components/Panel';
import ResultGridHeader from '../components/ResultGridHeader';

export default class BuildList extends Component {
  static propTypes = {
    buildList: PropTypes.arrayOf(PropTypes.object).isRequired,
    initialLoad: PropTypes.bool
  };

  render() {
    let {buildList, initialLoad} = this.props;
    return (
      <Panel>
        <ResultGridHeader>
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
            <Box width={2 / 12} style={{textAlign: 'right'}}>
              When
            </Box>
          </Flex>
        </ResultGridHeader>
        <div>
          {buildList.map(build => {
            return (
              <BuildListItem
                key={build.id}
                build={build}
                params={this.props.params}
                initialLoad={initialLoad}
              />
            );
          })}
        </div>
      </Panel>
    );
  }
}
