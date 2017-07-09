import Icon from 'react-icon-base';
import React, {Component} from 'react';
import styled from 'styled-components';

import NavHeading from './NavHeading';

export default class Login extends Component {
  render() {
    return (
      <Container>
        <Modal>
          <NavHeading>Login</NavHeading>
          <p>
            To continue you will need to first authenticate using your GitHub account.
          </p>
          <GitHubLogin href="/auth/github">
            <IconWrapper>
              <GitHubIcon size={15} />
            </IconWrapper>
            Login with GitHub
          </GitHubLogin>
        </Modal>
      </Container>
    );
  }
}

const Container = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
`;

const Modal = styled.div`
  border: 1px solid #ddd;
  max-width: 500px;
  padding: 20px;
  margin: 40px;
`;

const GitHubLogin = styled.a`
  color: #fff;
  background-color: #444;
  position: relative;
  padding: 6px 12px 6px 44px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  display: inline-block;
  margin-bottom: 0;
  font-size: 14px;
  font-weight: normal;
  line-height: 1.42857143;
  text-align: center;
  white-space: nowrap;
  vertical-align: middle;
  cursor: pointer;
  user-select: none;
  background-image: none;
  border: 1px solid rgba(0, 0, 0, 0.2);
  border-radius: 4px;
  text-decoration: none;
`;

const IconWrapper = styled.span`
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 28px;
  font-size: 1.6em;
  text-align: center;
  border-right: 1px solid rgba(0, 0, 0, 0.2);
`;

const GitHubIcon = props => {
  return (
    <Icon viewBox="0 0 15 15" {...props}>
      <g stroke="currentColor" strokeWidth="1" fill="none">
        <circle cx="7.5" cy="7.5" r="7" />
        <path d="M7.5,3.5 L7.5,7.5" strokeLinecap="round" strokeLinejoin="round" />
        <path
          d="M7.5,7.5 L9.51802643,9.55355183"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </g>
    </Icon>
  );
};
