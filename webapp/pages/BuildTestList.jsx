import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import Paginator from '../components/Paginator';
import Section from '../components/Section';
import AggregateTestList from '../components/AggregateTestList';

export default class BuildTestList extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    build: PropTypes.object.isRequired,
    repo: PropTypes.object.isRequired
  };

  getEndpoints() {
    let {repo} = this.context;
    let {buildNumber} = this.props.params;
    return [['testList', `/repos/${repo.full_name}/builds/${buildNumber}/tests`]];
  }

  renderBody() {
    return (
      <Section>
        <AggregateTestList
          repo={this.context.repo}
          build={this.context.build}
          testList={this.state.testList}
          params={this.props.params}
        />
        <Paginator links={this.state.testList.links} {...this.props} />
      </Section>
    );
  }
}
