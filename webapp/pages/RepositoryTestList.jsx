import React from 'react';

import AsyncPage from '../components/AsyncPage';
import TestList from '../components/TestList';

export default class RepositoryTestList extends AsyncPage {
  getEndpoints() {
    let {ownerName, repoName} = this.props.params;
    return [['testList', `/repos/${ownerName}/${repoName}/tests`]];
  }

  renderBody() {
    return <TestList testList={this.state.testList} />;
  }
}
