import React from 'react';
import styled from 'styled-components';
import {connect} from 'react-redux';
import {logout} from '../actions/auth';

import IconClock from '../assets/IconClock';
import Logo from '../assets/Logo';

const NavLink = styled.a`
  display: inline-block;
  width: 26px;
  height: 26px;
  margin: 5px 0;
  margin-right: 10px;
  cursor: pointer;

  &:last-child {
    margin-right: 0;
  }
`;

const Header = styled(props => {
  return (
    <div {...props}>
      <div style={{float: 'left', marginRight: 10}}>
        <NavLink to="/">
          <Logo size="26" />
        </NavLink>
      </div>
      {props.isAuthenticated &&
        <div style={{float: 'right'}}>
          <NavLink>
            <IconClock />
          </NavLink>
          <NavLink onClick={props.logout}>
            <IconClock />
          </NavLink>
        </div>}
      {props.children}
      <div style={{clear: 'both'}} />
    </div>
  );
})`
  background: #fff;
  padding: 20px 0 20px;
  margin: 0 20px 20px;
  border-bottom: 4px solid #111;
`;

export default connect(
  ({auth}) => ({
    user: auth.user,
    isAuthenticated: auth.isAuthenticated
  }),
  {logout}
)(Header);
