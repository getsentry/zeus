import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import Diff from '../components/Diff';
import Section from '../components/Section';

export default class BuildDiff extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    build: PropTypes.object.isRequired
  };

  getEndpoints() {
    let {buildNumber, ownerName, repoName} = this.props.params;
    return [['source', `/repos/${ownerName}/${repoName}/builds/${buildNumber}/source`]];
  }

  renderBody() {
    return (
      <Section>
        {this.state.source.diff
          ? <Diff diff={this.state.source.diff} />
          : <Section>
              <em>No source information was available for this build.</em>
            </Section>}
      </Section>
    );
  }
}
