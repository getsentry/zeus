import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import TabbedNav from '../components/TabbedNav';
import TabbedNavItem from '../components/TabbedNavItem';

export default class RepositoryTests extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  renderBody() {
    let {repo} = this.context;
    let basePath = `/${repo.full_name}/reports/tests`;
    return (
      <div>
        <TabbedNav>
          <TabbedNavItem to={`${basePath}`}>All Tests</TabbedNavItem>
          <TabbedNavItem to={`${basePath}/tree`} onlyActiveOnIndex={true}>
            Tree View
          </TabbedNavItem>
          <TabbedNavItem to={`${basePath}/time`}>Over Time</TabbedNavItem>
        </TabbedNav>
        {this.props.children}
      </div>
    );
  }
}
