import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {Flex, Box} from 'grid-styled';

import Panel from './Panel';
import ResultGridHeader from './ResultGridRow';
import ResultGridRow from './ResultGridRow';

export default class CoverageSummary extends Component {
  static propTypes = {
    coverage: PropTypes.arrayOf(PropTypes.object).isRequired
  };

  render() {
    return (
      <Panel>
        <ResultGridHeader>
          <Flex align="center">
            <Box flex="1" width={10 / 12} pr={15}>
              File
            </Box>
            <Box width={1 / 12} style={{textAlign: 'right'}}>
              Diff
            </Box>
            <Box width={1 / 12} style={{textAlign: 'right'}}>
              Overall
            </Box>
          </Flex>
        </ResultGridHeader>
        {this.props.coverage.map(fileCoverage => {
          return (
            <ResultGridRow key={fileCoverage.filename}>
              <Flex align="center">
                <Box flex="1" width={11 / 12} pr={15}>
                  {fileCoverage.filename}
                </Box>
                <Box width={1 / 12} style={{textAlign: 'right'}}>
                  {parseInt(
                    fileCoverage.lines_covered /
                      (fileCoverage.lines_covered + fileCoverage.lines_uncovered) *
                      1000,
                    10
                  ) / 10}%
                </Box>
                <Box width={1 / 12} style={{textAlign: 'right'}}>
                  {parseInt(
                    fileCoverage.diff_lines_covered /
                      (fileCoverage.diff_lines_covered +
                        fileCoverage.diff_lines_uncovered) *
                      1000,
                    10
                  ) / 10}%
                </Box>
              </Flex>
            </ResultGridRow>
          );
        })}
      </Panel>
    );
  }
}
