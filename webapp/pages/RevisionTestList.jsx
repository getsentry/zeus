import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import Section from '../components/Section';
import TestList from '../components/TestList';

export default class RevisionTestList extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    build: PropTypes.object.isRequired,
    repo: PropTypes.object.isRequired
  };

  getEndpoints() {
    let {repo} = this.context;
    let {sha} = this.props.params;
    return [['testList', `/repos/${repo.full_name}/revisions/${sha}/tests`]];
  }

  renderBody() {
    return (
      <Section>
        <TestList testList={this.state.testList} params={this.props.params} />
      </Section>
    );
  }
}
