import React, {Component} from 'react';
import PropTypes from 'prop-types';
import styled, {css} from 'styled-components';

import MdCheck from 'react-icons/lib/md/check-circle';
import MdClock from 'react-icons/lib/md/timer';
import MdError from 'react-icons/lib/md/error';

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
        {status != 'finished' && result === 'unknown' && <MdClock size="16" />}
        {result == 'passed' && <MdCheck size="16" />}
        {(result == 'failed' || result == 'aborted') && <MdError size="16" />}
      </ResultIcon>
    );
  }
}

export const ResultIcon = styled.div`
  display: inline-block;
  margin-right: 5px;

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
