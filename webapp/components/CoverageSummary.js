import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {Flex, Box} from 'grid-styled';

import Collapsable from './Collapsable';
import Panel from './Panel';
import ResultGridHeader from './ResultGridHeader';
import ResultGridRow from './ResultGridRow';

export default class CoverageSummary extends Component {
  static propTypes = {
    coverage: PropTypes.arrayOf(PropTypes.object).isRequired,
    collapsable: PropTypes.bool,
    maxVisible: PropTypes.number
  };

  static defaultProps = {
    collapsable: false
  };

  constructor(props, context) {
    super(props, context);
    this.state = {collapsable: props.collapsable};
  }

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
        <Collapsable
          collapsable={this.props.collapsable}
          maxVisible={this.props.maxVisible}>
          {this.props.coverage.map(fileCoverage => {
            let totalDiffLines =
              fileCoverage.diff_lines_covered + fileCoverage.diff_lines_uncovered;

            return (
              <ResultGridRow key={fileCoverage.filename}>
                <Flex align="center">
                  <Box flex="1" width={11 / 12} pr={15}>
                    {fileCoverage.filename}
                  </Box>
                  <Box width={1 / 12} style={{textAlign: 'right'}}>
                    {totalDiffLines
                      ? `${parseInt(
                          fileCoverage.diff_lines_covered / totalDiffLines * 1000,
                          10
                        ) / 10}%`
                      : ''}
                  </Box>
                  <Box width={1 / 12} style={{textAlign: 'right'}}>
                    {parseInt(
                      fileCoverage.lines_covered /
                        (fileCoverage.lines_covered + fileCoverage.lines_uncovered) *
                        1000,
                      10
                    ) / 10}%
                  </Box>
                </Flex>
              </ResultGridRow>
            );
          })}
        </Collapsable>
      </Panel>
    );
  }
}
