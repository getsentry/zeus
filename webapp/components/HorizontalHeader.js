import React, {Component} from 'react';
import {Link} from 'react-router';
import styled from 'styled-components';

import Logo from '../assets/Logo';

export default class HorizontalHeader extends Component {
  render() {
    return (
      <HeaderWrapper>
        <Link to="/" style={{height: 30}}>
          <Logo size="30" />
        </Link>
      </HeaderWrapper>
    );
  }
}

const HeaderWrapper = styled.div`
  background: #403b5d;
  color: #fff;
  padding: 15px 30px;
  height: 60px;
  box-shadow: inset -5px 0 10px rgba(0, 0, 0, .1);
`;
