import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import Content from '../components/Content';
import Header from '../components/Header';
import Nav, {NavItem} from '../components/Nav';
import requireAuth from '../utils/requireAuth';

export class Settings extends AsyncPage {
  static contextTypes = {
    repoList: PropTypes.arrayOf(PropTypes.object).isRequired,
    router: PropTypes.object.isRequired
  };

  getTitle() {
    return 'Settings';
  }

  render() {
    return (
      <div>
        <Header>
          <Nav>
            <NavItem to={'/settings/account'}>Account Details</NavItem>
            <NavItem to={'/settings/github/repos'}>Repositories</NavItem>
            <NavItem to={'/settings/token'}>API Access</NavItem>
          </Nav>
        </Header>

        <Content>{this.renderContent()}</Content>
      </div>
    );
  }

  renderBody() {
    return this.props.children;
  }
}

export default requireAuth(Settings);
