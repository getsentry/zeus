import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import TestList from '../components/TestList';

export default class RepositoryTestList extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  getEndpoints() {
    let {repo} = this.context;
    return [['testList', `/repos/${repo.full_name}/tests`]];
  }

  renderBody() {
    return <TestList testList={this.state.testList} />;
  }
}
