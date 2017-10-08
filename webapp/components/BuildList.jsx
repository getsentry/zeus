import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {Flex, Box} from 'grid-styled';

import BuildListItem from '../components/BuildListItem';
import Panel from '../components/Panel';
import ResultGridHeader from '../components/ResultGridHeader';

export default class BuildList extends Component {
  static propTypes = {
    buildList: PropTypes.arrayOf(PropTypes.object).isRequired,
    includeAuthor: PropTypes.bool,
    includeRepo: PropTypes.bool
  };

  render() {
    let {buildList, includeAuthor, includeRepo, params} = this.props;
    return (
      <Panel>
        <ResultGridHeader>
          <Flex>
            <Box flex="1" width={6 / 12} pr={15}>
              Build
            </Box>
            <Box width={1 / 12} style={{textAlign: 'center'}}>
              Coverage
            </Box>
            <Box width={1 / 12} style={{textAlign: 'center'}}>
              Duration
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
                params={params}
                includeAuthor={includeAuthor}
                includeRepo={includeRepo}
              />
            );
          })}
        </div>
      </Panel>
    );
  }
}
