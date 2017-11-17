import React from 'react';
import PropTypes from 'prop-types';

import ArtifactsList from '../components/ArtifactsList';
import AsyncPage from '../components/AsyncPage';
import CoverageSummary from '../components/CoverageSummary';
import JobList from '../components/JobList';
import Section from '../components/Section';
import SectionHeading from '../components/SectionHeading';
import SectionSubheading from '../components/SectionSubheading';
import StyleViolationList from '../components/StyleViolationList';
import TestList from '../components/TestList';

export default class BuildOverviewBase extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    build: PropTypes.object.isRequired,
    repo: PropTypes.object.isRequired
  };

  getEndpoints() {
    let endpoint = this.getBuildEndpoint();
    return [
      ['artifacts', `${endpoint}/artifacts`],
      ['jobList', `${endpoint}/jobs`],
      ['violationList', `${endpoint}/style-violations`],
      ['testFailures', `${endpoint}/tests?result=failed`],
      ['diffCoverage', `${endpoint}/file-coverage?diff_only=true`]
    ];
  }

  renderBody() {
    let failingJobs = this.state.jobList.filter(
      job => job.result == 'failed' && !job.allow_failure
    );

    let allowedFailures = this.state.jobList.filter(
      job => job.result == 'failed' && job.allow_failure
    );
    let unallowedFailures = this.state.jobList.filter(job => !job.allow_failure);
    return (
      <Section>
        {!!this.state.testFailures.length &&
          <div>
            <SectionHeading>Failing Tests</SectionHeading>
            <TestList
              testList={this.state.testFailures}
              params={this.props.params}
              collapsable={true}
            />
          </div>}
        {!!this.state.diffCoverage.length &&
          <div>
            <SectionHeading>Coverage</SectionHeading>
            <CoverageSummary coverage={this.state.diffCoverage} collapsable={true} />
          </div>}
        {!!this.state.violationList.length &&
          <div>
            <SectionHeading>Style Violations</SectionHeading>
            <StyleViolationList
              violationList={this.state.violationList}
              params={this.props.params}
              collapsable={true}
            />
          </div>}
        <div>
          <SectionHeading>
            Jobs
            {!!failingJobs.length &&
              <small>
                {' '}&mdash; {failingJobs.length} failed
              </small>}
          </SectionHeading>
          {!!unallowedFailures.length &&
            <div>
              <JobList build={this.context.build} jobList={unallowedFailures} />
            </div>}
          {!!allowedFailures.length &&
            <div>
              <SectionSubheading>Allowed Failures</SectionSubheading>
              <JobList build={this.context.build} jobList={allowedFailures} />
            </div>}
        </div>
        {!!this.state.artifacts.length &&
          <div>
            <SectionHeading>Artifacts</SectionHeading>
            <ArtifactsList artifacts={this.state.artifacts} collapsable={true} />
          </div>}
      </Section>
    );
  }
}
