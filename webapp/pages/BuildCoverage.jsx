import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import CoverageSummary from '../components/CoverageSummary';
import Section from '../components/Section';

export default class BuildCoverage extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    build: PropTypes.object.isRequired,
    repo: PropTypes.object.isRequired
  };

  getEndpoints() {
    let {repo} = this.context;
    let {buildNumber} = this.props.params;
    return [['coverage', `/repos/${repo.full_name}/builds/${buildNumber}/file-coverage`]];
  }

  shouldFetchUpdates() {
    return this.context.build.status !== 'finished';
  }

  renderBody() {
    return (
      <Section>
        <CoverageSummary coverage={this.state.coverage} />
      </Section>
    );
  }
}
