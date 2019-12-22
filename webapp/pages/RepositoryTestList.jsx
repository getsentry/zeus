import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import Paginator from '../components/Paginator';
import Section from '../components/Section';
import TestList from '../components/TestList';

export default class RepositoryTestList extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  getEndpoints() {
    let {repo} = this.context;
    return [['testList', `/repos/${repo.full_name}/tests`]];
  }

  renderBody() {
    return (
      <Section>
        <TestList testList={this.state.testList} />
        <Paginator links={this.state.testList.links} {...this.props} />
      </Section>
    );
  }
}
