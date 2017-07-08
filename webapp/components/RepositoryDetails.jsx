import React from 'react';
import PropTypes from 'prop-types';

import AsyncComponent from './AsyncComponent';
import Sidebar from './Sidebar';

export default class RepositoryDetails extends AsyncComponent {
  static contextTypes = {
    ...AsyncComponent.contextTypes,
    repoList: PropTypes.arrayOf(PropTypes.object).isRequired
  };

  static childContextTypes = {
    ...AsyncComponent.childContextTypes,
    repo: PropTypes.object.isRequired
  };

  getDefaultState(props, context) {
    let {repoID} = props.params;
    let {repoList} = context;
    let state = super.getDefaultState(props, context);
    state.repo = repoList.find(r => r.id === repoID);
    return state;
  }

  getChildContext() {
    return {repo: this.state.repo};
  }

  getTitle() {
    return this.state.repo.name;
  }

  renderBody() {
    return (
      <div>
        <Sidebar />
        {this.props.children}
      </div>
    );
  }
}
