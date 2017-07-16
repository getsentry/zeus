import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {Link} from 'react-router';
import styled from 'styled-components';

import Logo from '../assets/Logo';
import NavHeading from './NavHeading';
import SidebarLink from './SidebarLink';
import SidebarRepoItem from './SidebarRepoItem';

class RepositoryList extends Component {
  static contextTypes = {
    repoList: PropTypes.arrayOf(PropTypes.object).isRequired
  };

  render() {
    return (
      <div>
        {this.context.repoList.map(repo => {
          return <SidebarRepoItem key={repo.id} repo={repo} />;
        })}
      </div>
    );
  }
}

export default class Sidebar extends Component {
  render() {
    return (
      <SidebarWrapper>
        <div style={{marginBottom: 20}}>
          <Link to="/">
            <Logo size="30" />
          </Link>
        </div>
        <SidebarLink to="/builds">My Builds</SidebarLink>
        <SidebarNavHeading>
          Repositories <AddRepoLink to="/add-repository">Add</AddRepoLink>
        </SidebarNavHeading>
        <RepositoryList />
      </SidebarWrapper>
    );
  }
}

const AddRepoLink = styled(Link)`
  position: absolute;
  right: 0;
`;

const SidebarWrapper = styled.div`
  background: #39364e;
  color: #fff;
  padding: 18px 20px;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 220px;
  padding-top: linear-gradient(
    rgba(123, 107, 230, 0.10) 25%,
    rgba(118, 211, 146, 0.10) 100%
  );
  box-shadow: inset -5px 0 10px rgba(0, 0, 0, .1);
`;

const SidebarNavHeading = styled(NavHeading)`
  color: #8783A3;
  position: relative;
  margin-top: 20px;
  margin-bottom: 10px;
  font-weight: 400;
`;
