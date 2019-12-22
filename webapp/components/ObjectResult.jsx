import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {css} from '@emotion/core';
import styled from '@emotion/styled';

import Icon from './Icon';

import {
  MdCheckCircle,
  MdAvTimer,
  MdHistory,
  MdCancel,
  MdError,
  MdRemoveCircle,
  MdHelp
} from 'react-icons/md';

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
        return <MdHistory size={size} />;
      case 'in_progress':
        return <MdAvTimer size={size} />;
      default:
        if (status === 'finished' && result === 'unknown') return <MdHelp size={size} />;
        switch (result) {
          case 'passed':
            return <MdCheckCircle size={size} />;
          case 'aborted':
            return <MdCancel size={size} />;
          case 'failed':
            return <MdRemoveCircle size={size} />;
          case 'errored':
            return <MdError size={size} />;
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
      <ResultIcon status={status} result={result} mr>
        {this.getIcon(result, status)}
      </ResultIcon>
    );
  }
}

export const ResultIcon = styled(Icon)`
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
