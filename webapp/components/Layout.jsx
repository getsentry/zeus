import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {Flex, Box} from 'grid-styled';
import {Link} from 'react-router';
import {connect} from 'react-redux';
import styled from 'styled-components';

import MdClock from 'react-icons/lib/md/access-time';
import MdSettings from 'react-icons/lib/md/settings';
import MdLogout from 'react-icons/lib/md/exit-to-app';

import Content from './Content';
import Header from './Header';
import Footer from './Footer';
import Logo from '../assets/Logo';
import {logout} from '../actions/auth';

const Sidebar = styled(Box)`
  background: #39364e;
  padding: 10px 20px;
  color: #fff;
`;

const LogoArea = styled.div`
  padding: 4px 0 20px;
  margin: 0 0 20px;
  border-bottom: 4px solid #fff;
`;

const NavLink = styled(Link)`
  display: inline-block;
  color: #fff;
  width: 26px;
  height: 26px;
  margin-bottom: 10px;
  cursor: pointer;
  vertical-align: middle;

  &:last-child {
    margin-right: 0;
  }
`;

const ICON_SIZE = 26;

class Layout extends Component {
  static propTypes = {
    isAuthenticated: PropTypes.bool,
    logout: PropTypes.func.isRequired,
    children: PropTypes.node,
    title: PropTypes.string,
    withHeader: PropTypes.bool
  };

  render() {
    return (
      <Flex flexDirection="row" flex="1" style={{height: '100%'}}>
        <Sidebar flex="0 0 32px">
          <LogoArea>
            <Link to="/">
              <Logo size={ICON_SIZE} color="#fff" />
            </Link>
          </LogoArea>
          <div
            style={{
              flexDirection: 'column',
              height: '100%',
              display: 'flex'
            }}>
            <NavLink to="/builds">
              <MdClock size={ICON_SIZE} color="#fff" />
            </NavLink>
            <div style={{alignSelf: 'flex-end'}}>
              <NavLink to="/settings">
                <MdSettings size={ICON_SIZE} color="#fff" />
              </NavLink>
            </div>
            <div style={{alignSelf: 'flex-end'}}>
              {this.props.isAuthenticated && (
                <NavLink onClick={this.props.logout} style={{alignSelf: 'flex-end'}}>
                  <MdLogout size={ICON_SIZE} color="#fff" />
                </NavLink>
              )}
            </div>
          </div>
        </Sidebar>
        <Box flex="1 1 auto">
          {this.props.withHeader ? (
            <React.Fragment>
              <Header />
              <Content>{this.props.children}</Content>
              <Footer />
            </React.Fragment>
          ) : (
            this.props.children
          )}
        </Box>
      </Flex>
    );
  }
}

export default connect(
  ({auth}) => ({
    user: auth.user,
    isAuthenticated: auth.isAuthenticated
  }),
  {logout}
)(Layout);
