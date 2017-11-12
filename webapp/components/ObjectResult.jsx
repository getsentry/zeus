import React, {Component} from 'react';
import PropTypes from 'prop-types';
import styled, {css} from 'styled-components';

import PassedIcon from 'react-icons/lib/md/check-circle';
import InProgressIcon from 'react-icons/lib/md/av-timer';
import QueuedIcon from 'react-icons/lib/md/history';
import AbortedIcon from 'react-icons/lib/md/cancel';
import ErroredIcon from 'react-icons/lib/md/error';
import FailedIcon from 'react-icons/lib/md/remove-circle';
import UnknownIcon from 'react-icons/lib/md/help';

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
        {status == 'queued' && <QueuedIcon size="16" />}
        {status == 'in_progress' && <InProgressIcon size="16" />}
        {result == 'passed' && <PassedIcon size="16" />}
        {result == 'aborted' && <AbortedIcon size="16" />}
        {result == 'failed' && <FailedIcon size="16" />}
        {result == 'errored' && <ErroredIcon size="16" />}
        {status == 'finished' && result === 'unknown' && <UnknownIcon size="16" />}
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
