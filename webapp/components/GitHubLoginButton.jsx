import React, {Component} from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';

export default class GitHubLoginButton extends Component {
  static propTypes = {
    url: PropTypes.string,
    text: PropTypes.string
  };

  static defaultProps = {
    url: '/auth/github',
    text: 'Login with GitHub'
  };
  render() {
    let {url, text} = this.props;
    return (
      <GitHubLogin href={url}>
        {text}
      </GitHubLogin>
    );
  }
}

const GitHubLogin = styled.a`
  min-width: 150px;
  max-width: 250px;
  display: inline-block;
  margin: 1em;
  padding: 0.5em 1em;
  border: 2px solid #666;
  color: #666;
  border-radius: 4px;
  background: none;
  vertical-align: middle;
  position: relative;
  z-index: 1;
  -webkit-backface-visibility: hidden;
  -moz-osx-font-smoothing: grayscale;
  &:focus {
    outline: none;
  }
  &:hover {
    border-color: #111;
    color: #111;
  }
`;
