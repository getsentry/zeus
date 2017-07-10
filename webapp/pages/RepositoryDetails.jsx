import React from 'react';
import PropTypes from 'prop-types';

import AsyncComponent from '../components/AsyncComponent';

export default class RepositoryDetails extends AsyncComponent {
  static contextTypes = {
    ...AsyncComponent.contextTypes,
    repoList: PropTypes.arrayOf(PropTypes.object).isRequired
  };

  static childContextTypes = {
    ...AsyncComponent.childContextTypes,
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
    let {repoName} = props.params;
    let {repoList} = context;
    let state = super.getDefaultState(props, context);
    state.repo = repoList.find(r => r.name === repoName);
    return state;
  }

  getTitle() {
    return this.state.repo.name;
  }

  renderBody() {
    return (
      <div>
        {this.props.children}
      </div>
    );
  }
}
