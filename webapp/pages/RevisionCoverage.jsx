import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import BuildCoverage from '../components/BuildCoverage';
import Section from '../components/Section';

export default class RevisionCoverage extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  getEndpoints() {
    let {repo} = this.context;
    let {sha} = this.props.params;
    return [
      [
        'result',
        `/repos/${repo.full_name}/revisions/${sha}/file-coverage-tree`,
        {query: this.props.location.query}
      ]
    ];
  }

  renderBody() {
    return (
      <Section>
        <BuildCoverage
          result={this.state.result}
          repo={this.context.repo}
          {...this.props}
        />
      </Section>
    );
  }
}
