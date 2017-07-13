import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {Flex, Box} from 'grid-styled';

import ObjectDuration from './ObjectDuration';
import ObjectResult from './ObjectResult';
import Panel from './Panel';
import ResultGridRow from './ResultGridRow';

export default class TestList extends Component {
  static propTypes = {
    testList: PropTypes.arrayOf(PropTypes.object).isRequired
  };

  render() {
    return (
      <Panel>
        {this.props.testList.map(test => {
          return (
            <ResultGridRow key={test.name}>
              <Flex align="center">
                <Box flex="1" width={11 / 12} pr={15}>
                  <ObjectResult data={test} />
                  {test.name}
                </Box>
                <Box width={1 / 12} style={{textAlign: 'right'}}>
                  <ObjectDuration data={test} short={true} />
                </Box>
              </Flex>
            </ResultGridRow>
          );
        })}
      </Panel>
    );
  }
}
