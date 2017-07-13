import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import Section from '../components/Section';

export default class BuildDiff extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    build: PropTypes.object.isRequired
  };

  getEndpoints() {
    let {buildNumber, repoName} = this.props.params;
    return [['source', `/repos/${repoName}/builds/${buildNumber}/source`]];
  }

  renderBody() {
    return (
      <Section>
        {this.state.source.diff ||
          <em>No source information was available for this build.</em>}
      </Section>
    );
  }
}
