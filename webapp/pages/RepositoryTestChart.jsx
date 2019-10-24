import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import Section from '../components/Section';
import TestChart from '../components/TestChart';

export default class RepositoryTestChart extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  getEndpoints() {
    let {repo} = this.context;
    return [['testList', `/repos/${repo.full_name}/tests-by-job`]];
  }

  renderBody() {
    return (
      <Section>
        <TestChart testList={this.state.testList} />
      </Section>
    );
  }
}