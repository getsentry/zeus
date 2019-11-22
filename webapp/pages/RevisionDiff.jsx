import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import Diff from '../components/Diff';
import Section from '../components/Section';

export default class RevisionDiff extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired,
    build: PropTypes.object.isRequired
  };

  getEndpoints() {
    let {repo} = this.context;
    let {sha} = this.props.params;
    return [['diff', `/repos/${repo.full_name}/revisions/${sha}/diff`]];
  }

  renderBody() {
    return (
      <Section>
        {this.state.diff.diff ? (
          <Diff diff={this.state.diff.diff} />
        ) : (
          <Section>
            <em>No diff information was available for this build.</em>
          </Section>
        )}
      </Section>
    );
  }
}
