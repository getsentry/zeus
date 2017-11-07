import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {Flex, Box} from 'grid-styled';

import Collapsable from './Collapsable';
import Panel from './Panel';
import ResultGridHeader from './ResultGridHeader';
import ResultGridRow from './ResultGridRow';

export default class ArtifactsList extends Component {
  static propTypes = {
    artifacts: PropTypes.arrayOf(PropTypes.object).isRequired,
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

  getTypeName(type) {
    if (!type) {
      return '';
    }

    return type
      .toLowerCase()
      .replace(/^.|_+[^_]/g, txt => ' ' + txt.slice(-1).toUpperCase())
      .replace(/_/g, '');
  }

  render() {
    return (
      <Panel>
        <ResultGridHeader>
          <Flex align="center">
            <Box flex="1" width={9 / 12} pr={15}>
              File
            </Box>
            <Box width={2 / 12}>Type</Box>
            <Box width={1 / 12} style={{textAlign: 'right'}}>
              Size
            </Box>
          </Flex>
        </ResultGridHeader>
        <Collapsable
          collapsable={this.props.collapsable}
          maxVisible={this.props.maxVisible}>
          {this.props.artifacts.map(artifact => {
            return (
              <ResultGridRow key={artifact.id}>
                <Flex align="center">
                  <Box flex="1" width={9 / 12} pr={15}>
                    <div>
                      {this.props.collapsable ? (
                        artifact.name
                      ) : (
                        <a href={artifact.download_url}>{artifact.name}</a>
                      )}
                    </div>
                  </Box>
                  <Box width={2 / 12}>{this.getTypeName(artifact.type)}</Box>
                  <Box width={2 / 12} style={{textAlign: 'right'}}>
                    {/* TODO: Show the file size here */}
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
