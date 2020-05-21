import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {Link} from 'react-router';
import styled from '@emotion/styled';
import {connect} from 'react-redux';
import Select from 'react-select';

import {logout} from '../actions/auth';
import Logo from '../assets/Logo';

import {MdExitToApp, MdSettings} from 'react-icons/md';

const NavLink = styled(Link)`
  display: inline-block;
  width: 26px;
  height: 26px;
  margin: 5px 0;
  margin-right: 10px;
  cursor: pointer;
  vertical-align: middle;

  &:last-child {
    margin-right: 0;
  }
`;

class UnstyledHeader extends Component {
  static contextTypes = {
    repo: PropTypes.object,
    repoList: PropTypes.arrayOf(PropTypes.object).isRequired,
    router: PropTypes.object.isRequired
  };

  getRepositoryList() {
    return this.context.repoList.map(repo => {
      return {value: repo.full_name, label: `${repo.owner_name} / ${repo.name}`};
    });
  }

  onSelectRepo = node => {
    if (!node) return;
    this.context.router.push(`/${node.value}`);
  };

  getActiveRepo() {
    let {repo} = this.context;
    if (!repo) return null;
    return {value: repo.full_name, label: `${repo.owner_name} / ${repo.name}`};
  }

  render() {
    let props = this.props;
    return (
      <div className={props.className}>
        <div style={{float: 'left', marginRight: 10}}>
          <NavLink to="/">
            <Logo size="26" />
          </NavLink>
        </div>
        {props.isAuthenticated && (
          <div style={{float: 'right'}}>
            <NavLink to="/settings">
              <MdSettings size={24} />
            </NavLink>
            <NavLink onClick={props.logout}>
              <MdExitToApp size={24} />
            </NavLink>
          </div>
        )}
        <Select
          placeholder="Select Repository"
          className="Repo-Selector"
          clearable={false}
          options={this.getRepositoryList()}
          noOptionsMessage={() => '(no repos configured)'}
          onChange={this.onSelectRepo}
          value={this.getActiveRepo()}
          styles={{
            option: provided => ({
              ...provided,
              cursor: 'pointer'
            })
          }}
        />
        {props.children}
        <div style={{clear: 'both'}} />
      </div>
    );
  }
}

const Header = styled(UnstyledHeader)`
  background: #fff;
  padding: 10px 0 10px;
  margin: 0 20px 20px;
  border-bottom: 4px solid #111;

  .Repo-Selector {
    vertical-align: top;
    display: inline-block;
    width: 100%;
    max-width: 300px;
    cursor: pointer;
    margin-right: 20px;
    /* float: left;
    font-size: 24px;
    margin: 0;
    line-height: 36px;
    letter-spacing: -1px;
    text-transform: uppercase;
    font-weight: 500; */
  }
`;

export default connect(
  ({auth}) => ({
    user: auth.user,
    isAuthenticated: auth.isAuthenticated
  }),
  {logout}
)(Header);
