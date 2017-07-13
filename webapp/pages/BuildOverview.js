import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import JobList from '../components/JobList';
import Section from '../components/Section';
import SectionHeading from '../components/SectionHeading';
import TestList from '../components/TestList';

export default class BuildJobList extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    build: PropTypes.object.isRequired
  };

  getEndpoints() {
    let {buildNumber, repoName} = this.props.params;
    return [
      ['jobList', `/repos/${repoName}/builds/${buildNumber}/jobs`],
      ['testFailures', `/repos/${repoName}/builds/${buildNumber}/tests?result=failed`]
    ];
  }

  renderBody() {
    return (
      <div>
        <Section>
          <SectionHeading>Failing Tests</SectionHeading>
          <TestList testList={this.state.testFailures} />
        </Section>
        <Section>
          <SectionHeading>Jobs</SectionHeading>
          <JobList build={this.context.build} jobList={this.state.jobList} />
        </Section>
      </div>
    );
  }
}
