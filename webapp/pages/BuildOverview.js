import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import CoverageSummary from '../components/CoverageSummary';
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
      ['testFailures', `/repos/${repoName}/builds/${buildNumber}/tests?result=failed`],
      [
        'diffCoverage',
        `/repos/${repoName}/builds/${buildNumber}/file-coverage?diff_only=true`
      ]
    ];
  }

  renderBody() {
    return (
      <div>
        <Section>
          <SectionHeading>Coverage</SectionHeading>
          <CoverageSummary coverage={this.state.diffCoverage} />
        </Section>
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
