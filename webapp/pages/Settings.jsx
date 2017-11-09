import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import Content from '../components/Content';
import Header from '../components/Header';
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
      <div>
        <Header>
          <Nav>
            <NavItem to={'/settings/github/repos'}>Repositories</NavItem>
            <NavItem to={'/settings/token'}>API Token</NavItem>
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
