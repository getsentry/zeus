import React, {Component} from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';

import Collapsable from './Collapsable';
import {ResultGrid, Column, Header, Row} from './ResultGrid';

class ViolationListItem extends Component {
  static propTypes = {
    violation: PropTypes.object.isRequired
  };

  render() {
    let {violation} = this.props;
    return (
      <ViolationListItemWrapper className={`severity-${violation.severity}`}>
        <Row>
          <Column>{violation.message}</Column>
          <Column textAlign="left">{violation.filename}</Column>
          <Column textAlign="right" width={80}>
            {violation.lineno !== null ? violation.lineno.toLocaleString() : ''}
          </Column>
          <Column textAlign="right" width={80}>
            {violation.colno !== null ? violation.colno.toLocaleString() : ''}
          </Column>
        </Row>
      </ViolationListItemWrapper>
    );
  }
}

export default class StyleViolationList extends Component {
  static propTypes = {
    violationList: PropTypes.arrayOf(PropTypes.object).isRequired,
    collapsable: PropTypes.bool,
    maxVisible: PropTypes.number,
    params: PropTypes.object
  };

  static defaultProps = {collapsable: false};

  render() {
    return (
      <ResultGrid>
        <Header>
          <Column>Violation</Column>
          <Column textAlign="left">Filename</Column>
          <Column textAlign="right" width={80}>
            Line
          </Column>
          <Column textAlign="right" width={80}>
            Column
          </Column>
        </Header>
        <Collapsable
          collapsable={this.props.collapsable}
          maxVisible={this.props.maxVisible}>
          {this.props.violationList.map(violation => {
            return (
              <ViolationListItem
                params={this.props.params}
                violation={violation}
                key={violation.id}
              />
            );
          })}
        </Collapsable>
      </ResultGrid>
    );
  }
}

const ViolationListItemWrapper = styled.div`
  &.severity-error {
    background: #ffe9e9;
  }

  &.severity-warning {
    background: #ffedde;
  }
`;
