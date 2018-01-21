import React, {Component} from 'react';
import PropTypes from 'prop-types';

import Header from '../components/Header';
import Nav, {NavItem} from '../components/Nav';

export default class RepositoryHeader extends Component {
  static contextTypes = {
    repo: PropTypes.object.isRequired
  };

  render() {
    let {repo} = this.context;
    let basePath = `/${repo.full_name}`;

    return (
      <Header>
        <Nav>
          <NavItem to={basePath} onlyActiveOnIndex={true}>
            Commits
          </NavItem>
          <NavItem to={`${basePath}/builds`}>Builds</NavItem>
          <NavItem to={`${basePath}/coverage`}>Coverage</NavItem>
          <NavItem to={`${basePath}/tests`}>Tests</NavItem>
          <NavItem to={`${basePath}/stats`}>Stats</NavItem>
          {repo.permission === 'admin' && (
            <NavItem to={`${basePath}/settings`}>Settings</NavItem>
          )}
        </Nav>
      </Header>
    );
  }
}
