import React from 'react';

import AsyncPage from '../components/AsyncPage';
import Section from '../components/Section';
import TestList from '../components/TestList';

export default class BuildTestList extends AsyncPage {
  getEndpoints() {
    let {buildNumber, ownerName, repoName} = this.props.params;
    return [['testList', `/repos/${ownerName}/${repoName}/builds/${buildNumber}/tests`]];
  }

  renderBody() {
    return (
      <Section>
        <TestList testList={this.state.testList} params={this.props.params} />
      </Section>
    );
  }
}
