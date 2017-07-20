import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import Content from '../components/Content';
import Sidebar from '../components/Sidebar';

export default class RepositoryDetails extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repoList: PropTypes.arrayOf(PropTypes.object).isRequired
  };

  static childContextTypes = {
    ...AsyncPage.childContextTypes,
    ...RepositoryDetails.contextTypes,
    repo: PropTypes.object.isRequired
  };

  getChildContext() {
    return {
      ...this.context,
      repo: this.state.repo
    };
  }

  getDefaultState(props, context) {
    let {ownerName, repoName} = props.params;
    let {repoList} = context;
    let state = super.getDefaultState(props, context);
    state.repo = repoList.find(r => r.owner_name === ownerName && r.name === repoName);
    return state;
  }

  getTitle() {
    let {repo} = this.state;
    return `${repo.owner_name}/${repo.name}`;
  }

  renderBody() {
    return (
      <div>
        <Sidebar params={this.props.params} />
        <Content>
          {this.props.children}
        </Content>
      </div>
    );
  }
}
