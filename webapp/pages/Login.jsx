import React, {Component} from 'react';
import styled from 'styled-components';

import Modal from '../components/Modal';

export default class Login extends Component {
  render() {
    return (
      <Modal title="Login">
        <p>To continue you will need to first authenticate using your GitHub account.</p>
        <p style={{textAlign: 'center', marginBottom: 0}}>
          <GitHubLogin href="/auth/github">Login with GitHub</GitHubLogin>
        </p>
      </Modal>
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
