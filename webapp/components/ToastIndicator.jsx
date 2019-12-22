import React, {Component} from 'react';
import PropTypes from 'prop-types';
import classNames from 'classnames';
import styled from '@emotion/styled';

class ToastIndicator extends Component {
  static propTypes = {
    className: PropTypes.string,
    children: PropTypes.node,
    type: PropTypes.string
  };

  static defaultProps = {
    type: 'info'
  };

  render() {
    return (
      <div className={classNames('toast', this.props.type, this.props.className)}>
        <span className="icon" />
        <div className="toast-message">{this.props.children}</div>
      </div>
    );
  }
}

const StyledToastIndicator = styled(ToastIndicator)`
  margin: 4px 0;
  font-size: 13px;
  padding: 20px 30px;
  font-size: 15px;
  z-index: 100000;
  border-radius: 3px;

  position: fixed;
  bottom: 20px;
  right: 20px;
  color: #fff;
  opacity: 1;

  &.loading .toast-message {
    display: inline-block;
    padding-left: 25px;
  }

  &.loading {
    background: rgba(52, 60, 69, 0.8);
  }
  &.loading.fade-exit {
    opacity: 0;
    display: none; /* hides immediately*/
  }

  &.loading .icon {
    text-indent: -9999em;
    border: 2px solid rgba(255, 255, 255, 0.4);
    border-left-color: rgba(255, 255, 255, 1);
    -webkit-animation: loading 0.5s infinite linear;
    animation: loading 0.55s infinite linear;
    margin: 0;
    border-radius: 50%;
    width: 20px;
    height: 20px;
    position: absolute;
    top: 20px;
    left: 20px;
  }

  &.success {
    background: green;
    color: white;
  }
  &.error {
    background: red;
    color: white;
  }

  .fade-enter {
    opacity: 1;
  }
  .fade-exit {
    opacity: 1;
  }
  .fade-enter-active {
    opacity: 1;
    transition: opacity 200ms;
  }
  .fade-exit-active {
    opacity: 0.01;
    transition: opacity 200ms;
  }

  @-webkit-keyframes loading {
    0% {
      -webkit-transform: rotate(0deg);
      transform: rotate(0deg);
    }
    100% {
      -webkit-transform: rotate(360deg);
      transform: rotate(360deg);
    }
  }
  @keyframes loading {
    0% {
      -webkit-transform: rotate(0deg);
      transform: rotate(0deg);
    }
    100% {
      -webkit-transform: rotate(360deg);
      transform: rotate(360deg);
    }
  }
`;

export default StyledToastIndicator;
