import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {Link} from 'react-router';
import styled from 'styled-components';

import {Breadcrumbs, CrumbLink} from '../components/Breadcrumbs';
import Header from '../components/Header';

const Nav = styled.div`float: right;`;

const NavItem = styled(Link)`
  cursor: pointer;
  float: left;
  font-size: 15px;
  color: #AAA7BB;
  margin-left: 10px;
  padding: 5px 10px;

  &.active {
    background: #7B6BE6;
    color: #fff;
  }

  &.${props => props.activeClassName} {
    background: #7B6BE6;
    color: #fff;
  }
`;

NavItem.defaultProps = {
  activeClassName: 'active'
};

export default class RepositoryHeader extends Component {
  static contextTypes = {
    repo: PropTypes.object.isRequired
  };

  render() {
    let {repo} = this.context;
    let basePath = `/${repo.full_name}`;

    let children =
      this.props.children ||
      <Breadcrumbs>
        <CrumbLink to={`/${repo.provider}/${repo.owner_name}`}>
          {repo.owner_name}
        </CrumbLink>
        <CrumbLink to={basePath}>
          {repo.name}
        </CrumbLink>
      </Breadcrumbs>;
    return (
      <Header>
        <div style={{float: 'left'}}>
          {children}
        </div>
        <Nav>
          <NavItem to={basePath} onlyActiveOnIndex={true}>
            Commits
          </NavItem>
          <NavItem to={`${basePath}/builds`}>Builds</NavItem>
          <NavItem to={`${basePath}/tests`}>Tests</NavItem>
          <NavItem to={`${basePath}/settings`}>Settings</NavItem>
        </Nav>
      </Header>
    );
  }
}
