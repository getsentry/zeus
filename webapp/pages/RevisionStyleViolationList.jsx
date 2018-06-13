import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import Section from '../components/Section';
import StyleViolationList from '../components/StyleViolationList';

export default class RevisionStyleViolationList extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    build: PropTypes.object.isRequired,
    repo: PropTypes.object.isRequired
  };

  getEndpoints() {
    let {repo} = this.context;
    let {sha} = this.props.params;
    return [
      ['violationList', `/repos/${repo.full_name}/revisions/${sha}/style-violations`]
    ];
  }

  renderBody() {
    return (
      <Section>
        <StyleViolationList
          violationList={this.state.violationList}
          params={this.props.params}
        />
      </Section>
    );
  }
}
