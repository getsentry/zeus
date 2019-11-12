import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {Flex, Box} from '@rebass/grid/emotion';
import styled from '@emotion/styled';

import Collapsable from './Collapsable';
import FileSize from './FileSize';
import {ResultGrid, Column, Header} from './ResultGrid';
import ResultGridRow from './ResultGridRow';

class BundleListItem extends Component {
  static propTypes = {
    params: PropTypes.object,
    bundle: PropTypes.object.isRequired
  };

  render() {
    let {bundle} = this.props;
    return (
      <BundleListItemWrapper>
        <ResultGridRow>
          <Flex align="center">
            <Box flex="1">
              <strong>{bundle.name}</strong>
            </Box>
            <Box width={90} style={{textAlign: 'right'}}>
              <strong>
                <FileSize
                  value={bundle.assets.map(a => a.size).reduce((a, b) => a + b, 0)}
                />
              </strong>
            </Box>
          </Flex>
          {!!bundle.assets.length && (
            <BundleDetailsWrapper>
              {bundle.assets.map(asset => {
                return (
                  <Flex align="center" key={asset.name} className="asset">
                    <Box flex="1">{asset.name}</Box>
                    <Box width={90} style={{textAlign: 'right'}}>
                      <FileSize value={asset.size} />
                    </Box>
                  </Flex>
                );
              })}
            </BundleDetailsWrapper>
          )}
        </ResultGridRow>
      </BundleListItemWrapper>
    );
  }
}

export default class BundleList extends Component {
  static propTypes = {
    bundleList: PropTypes.arrayOf(PropTypes.object).isRequired,
    collapsable: PropTypes.bool,
    maxVisible: PropTypes.number,
    params: PropTypes.object
  };

  static defaultProps = {collapsable: false};

  render() {
    return (
      <ResultGrid>
        <Header>
          <Column>Bundle</Column>
          <Column textAlign="right" width={80}>
            Size
          </Column>
        </Header>
        <Collapsable
          collapsable={this.props.collapsable}
          maxVisible={this.props.maxVisible}>
          {this.props.bundleList.map(bundle => {
            return (
              <BundleListItem
                params={this.props.params}
                bundle={bundle}
                key={bundle.name}
              />
            );
          })}
        </Collapsable>
      </ResultGrid>
    );
  }
}

const BundleListItemWrapper = styled.div``;

const BundleDetailsWrapper = styled.div`
  color: #666;
  font-size: 13px;
  line-height: 1.4em;

  .asset {
    margin-top: 10px;
  }
`;
