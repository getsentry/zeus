import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import CoverageSummary from '../components/CoverageSummary';
import Section from '../components/Section';

export default class RevisionCoverage extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    build: PropTypes.object.isRequired,
    repo: PropTypes.object.isRequired
  };

  getEndpoints() {
    let {repo} = this.context;
    let {sha} = this.props.params;
    return [['coverage', `/repos/${repo.full_name}/revisions/${sha}/file-coverage`]];
  }

  renderBody() {
    return (
      <Section>
        <CoverageSummary
          coverage={this.state.coverage}
          repo={this.context.repo}
          build={this.props.build}
        />
      </Section>
    );
  }
}
