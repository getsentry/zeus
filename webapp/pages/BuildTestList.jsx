import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import Section from '../components/Section';
import TestList from '../components/TestList';

export default class BuildTestList extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  getEndpoints() {
    let {repo} = this.context;
    let {buildNumber} = this.props.params;
    return [['testList', `/repos/${repo.full_name}/builds/${buildNumber}/tests`]];
  }

  renderBody() {
    return (
      <Section>
        <TestList testList={this.state.testList} params={this.props.params} />
      </Section>
    );
  }
}
