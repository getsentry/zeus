import React from 'react';

import AsyncPage from '../components/AsyncPage';
import Section from '../components/Section';
import TestList from '../components/TestList';

export default class BuildTestList extends AsyncPage {
  getEndpoints() {
    let {buildNumber, orgName, projectName} = this.props.params;
    return [
      ['testList', `/projects/${orgName}/${projectName}/builds/${buildNumber}/tests`]
    ];
  }

  renderBody() {
    return (
      <Section>
        <TestList testList={this.state.testList} params={this.props.params} />
      </Section>
    );
  }
}
