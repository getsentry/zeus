import React, {Component} from 'react';
import PropTypes from 'prop-types';
import styled, {css} from 'styled-components';

import IconCircleCheck from '../assets/IconCircleCheck';
import IconCircleCross from '../assets/IconCircleCross';

export default class ObjectResult extends Component {
  static propTypes = {
    data: PropTypes.shape({
      result: PropTypes.string.isRequired,
      status: PropTypes.string
    })
  };

  render() {
    if (!this.props.data) {
      return null;
    }
    let {result, status} = this.props.data;
    return (
      <ResultIcon status={status} result={result}>
        {result == 'passed' && <IconCircleCheck size="15" />}
        {result == 'failed' && <IconCircleCross size="15" />}
      </ResultIcon>
    );
  }
}

export const ResultIcon = styled.div`
  display: inline-block;
  margin-right: 10px;

  ${props => {
    switch (props.result) {
      case 'passed':
        return css`
          svg {
            color: #76D392;
          }
        `;
      case 'failed':
        return css`
          color: #F06E5B;
          svg {
            color: #F06E5B;
          }
        `;
      default:
        return css`
          svg {
            color: #BFBFCB;
          }
        `;
    }
  }};
`;
