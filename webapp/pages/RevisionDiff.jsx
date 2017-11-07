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
    return [['source', `/repos/${repo.full_name}/revisions/${sha}/source`]];
  }

  renderBody() {
    return (
      <Section>
        {this.state.source.diff ? (
          <Diff diff={this.state.source.diff} />
        ) : (
          <Section>
            <em>No source information was available for this build.</em>
          </Section>
        )}
      </Section>
    );
  }
}
