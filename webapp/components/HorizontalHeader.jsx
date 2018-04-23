import React, {Component} from 'react';
import {Link} from 'react-router';
import styled from 'styled-components';

import Logo from '../assets/Logo';

export class HorizontalHeader extends Component {
  render() {
    return (
      <HeaderWrapper>
        <Link to="/" style={{height: 30, marginRight: 10}}>
          <Logo size="30" />
        </Link>
        {this.props.children}
      </HeaderWrapper>
    );
  }
}

export const HeaderWrapper = styled.div`
  background: #403b5d;
  color: #fff;
  padding: 15px 30px;
  height: 60px;
  box-shadow: inset -5px 0 10px rgba(0, 0, 0, 0.1);
`;

export const HeaderLink = styled(Link)`
  color: #8783a3;
  font-weight: 400;
`;

export default HorizontalHeader;
