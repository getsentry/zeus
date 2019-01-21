import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import Layout from '../components/Layout';
import RepositoryContent from '../components/RepositoryContent';
import RepositoryHeader from '../components/RepositoryHeader';

export default class RepositoryDetails extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repoList: PropTypes.arrayOf(PropTypes.object).isRequired
  };

  static childContextTypes = {
    ...AsyncPage.childContextTypes,
    ...RepositoryDetails.contextTypes,
    repo: PropTypes.object
  };

  getChildContext() {
    return {
      ...this.context,
      repo: this.state.repo
    };
  }

  getDefaultState(props, context) {
    let {provider, ownerName, repoName} = props.params;
    let {repoList} = context;
    let state = super.getDefaultState(props, context);
    state.repo =
      repoList.find(
        r => r.provider === provider && r.owner_name === ownerName && r.name === repoName
      ) || null;
    state.hasCachedRepo = !!state.repo;
    state.loading = !state.hasCachedRepo;
    return state;
  }

  getEndpoints() {
    if (!this.state || this.state.hasCachedRepo) return [];
    let {provider, ownerName, repoName} = this.props.params;
    return [['repo', `/repos/${provider}/${ownerName}/${repoName}`]];
  }

  getTitle() {
    let {repo} = this.state;
    return repo ? `${repo.owner_name}/${repo.name}` : null;
  }

  renderBody() {
    return (
      <Layout>
        <RepositoryHeader />
        <RepositoryContent>{this.props.children}</RepositoryContent>
      </Layout>
    );
  }
}
