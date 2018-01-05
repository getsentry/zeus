import React, {Component} from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';

import Collapsable from './Collapsable';
import FileSize from './FileSize';
import {ResultGrid, Column, Header, Row} from './ResultGrid';

class BundleListItem extends Component {
  static propTypes = {
    bundle: PropTypes.object.isRequired
  };

  render() {
    let {bundle} = this.props;
    return (
      <BundleListItemWrapper>
        <Row>
          <Column>
            {bundle.name}
          </Column>
          <Column textAlign="right" width={80}>
            <FileSize value={bundle.assets.map(a => a.size).reduce((a, b) => a + b, 0)} />
          </Column>
        </Row>
      </BundleListItemWrapper>
    );
  }
}

export default class BundleList extends Component {
  static propTypes = {
    bundleList: PropTypes.arrayOf(PropTypes.object).isRequired,
    collapsable: PropTypes.bool,
    maxVisible: PropTypes.number
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

const BundleListItemWrapper = styled.div`
  &.severity-error {
    background: #ffe9e9;
  }

  &.severity-warning {
    background: #ffedde;
  }
`;
