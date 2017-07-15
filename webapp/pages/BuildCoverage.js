import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import CoverageSummary from '../components/CoverageSummary';
import Section from '../components/Section';

export default class BuildCoverage extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    build: PropTypes.object.isRequired
  };

  getEndpoints() {
    let {buildNumber, orgName, projectName} = this.props.params;
    return [
      [
        'coverage',
        `/projects/${orgName}/${projectName}/builds/${buildNumber}/file-coverage`
      ]
    ];
  }

  renderBody() {
    return (
      <Section>
        <CoverageSummary coverage={this.state.coverage} />
      </Section>
    );
  }
}
