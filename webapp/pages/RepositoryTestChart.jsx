import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import Paginator from '../components/Paginator';
import Section from '../components/Section';
import TestChart from '../components/TestChart';

export default class RepositoryTestChart extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  getEndpoints() {
    let {repo} = this.context;
    return [
      [
        'results',
        `/repos/${repo.full_name}/tests-by-build`,
        {query: this.props.location.query}
      ]
    ];
  }

  renderBody() {
    return (
      <Section>
        <TestChart results={this.state.results} repo={this.context.repo} />
        <Paginator links={this.state.results.links} {...this.props} />
      </Section>
    );
  }
}
