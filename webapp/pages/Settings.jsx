import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import Content from '../components/Content';
import Header from '../components/Header';
import Layout from '../components/Layout';
import Nav, {NavItem} from '../components/Nav';

export default class Settings extends AsyncPage {
  static contextTypes = {
    repoList: PropTypes.arrayOf(PropTypes.object).isRequired,
    router: PropTypes.object.isRequired
  };

  getTitle() {
    return 'Settings';
  }

  render() {
    return (
      <Layout title="Settings">
        <Header>
          <Nav>
            <NavItem to={'/settings/account'}>Account Details</NavItem>
            <NavItem to={'/settings/github/repos'}>Repositories</NavItem>
            <NavItem to={'/settings/token'}>API Access</NavItem>
          </Nav>
        </Header>

        <Content>{this.renderContent()}</Content>
      </Layout>
    );
  }

  renderBody() {
    return this.props.children;
  }
}
