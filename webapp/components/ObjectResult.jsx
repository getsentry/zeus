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
    }),
    size: PropTypes.number
  };

  static defaultProps = {
    size: 16
  };

  getIcon(result, status) {
    let {size} = this.props;
    switch (status) {
      case 'queued':
        return <QueuedIcon size={size} />;
      case 'in_progress':
        return <InProgressIcon size={size} />;
      default:
        if (status === 'finished' && result === 'unknown')
          return <UnknownIcon size={size} />;
        switch (result) {
          case 'passed':
            return <PassedIcon size={size} />;
          case 'aborted':
            return <AbortedIcon size={size} />;
          case 'failed':
            return <FailedIcon size={size} />;
          case 'errored':
            return <ErroredIcon size={size} />;
          default:
            return null;
        }
    }
  }

  render() {
    if (!this.props.data) {
      return null;
    }
    let {result, status} = this.props.data;
    return (
      <ResultIcon status={status} result={result}>
        {this.getIcon(result, status)}
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
            color: #76d392;
          }
        `;
      case 'errored':
        return css`
          color: #f0a05b;
          svg {
            color: #f0a05b;
          }
        `;
      case 'failed':
        return css`
          color: #f05b5b;
          svg {
            color: #f05b5b;
          }
        `;
      default:
        return css`
          svg {
            color: #bfbfcb;
          }
        `;
    }
  }};
`;
