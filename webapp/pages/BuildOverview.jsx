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
    let {buildNumber, ownerName, repoName} = this.props.params;
    return [
      ['jobList', `/repos/${ownerName}/${repoName}/builds/${buildNumber}/jobs`],
      [
        'testFailures',
        `/repos/${ownerName}/${repoName}/builds/${buildNumber}/tests?result=failed`
      ],
      [
        'diffCoverage',
        `/repos/${ownerName}/${repoName}/builds/${buildNumber}/file-coverage?diff_only=true`
      ]
    ];
  }

  renderBody() {
    return (
      <Section>
        {this.state.testFailures.length !== 0 &&
          <div>
            <SectionHeading>Failing Tests</SectionHeading>
            <TestList
              testList={this.state.testFailures}
              params={this.props.params}
              collapsable={true}
            />
          </div>}
        <div>
          <SectionHeading>Coverage</SectionHeading>
          <CoverageSummary coverage={this.state.diffCoverage} collapsable={true} />
        </div>
        <div>
          <SectionHeading>Jobs</SectionHeading>
          <JobList build={this.context.build} jobList={this.state.jobList} />
        </div>
      </Section>
    );
  }
}
