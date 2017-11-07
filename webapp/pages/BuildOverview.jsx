import React from 'react';
import PropTypes from 'prop-types';

import ArtifactsList from '../components/ArtifactsList';
import AsyncPage from '../components/AsyncPage';
import CoverageSummary from '../components/CoverageSummary';
import JobList from '../components/JobList';
import Section from '../components/Section';
import SectionHeading from '../components/SectionHeading';
import SectionSubheading from '../components/SectionSubheading';
import TestList from '../components/TestList';

export default class BuildOverview extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    build: PropTypes.object.isRequired,
    repo: PropTypes.object.isRequired
  };

  getEndpoints() {
    let {repo} = this.context;
    let {buildNumber} = this.props.params;
    return [
      ['artifacts', `/repos/${repo.full_name}/builds/${buildNumber}/artifacts`],
      ['jobList', `/repos/${repo.full_name}/builds/${buildNumber}/jobs`],
      [
        'testFailures',
        `/repos/${repo.full_name}/builds/${buildNumber}/tests?result=failed`
      ],
      [
        'diffCoverage',
        `/repos/${repo.full_name}/builds/${buildNumber}/file-coverage?diff_only=true`
      ]
    ];
  }

  shouldFetchUpdates() {
    return this.context.build.status !== 'finished';
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
        {this.state.artifacts.length !== 0 && (
          <div>
            <SectionHeading>Artifacts</SectionHeading>
            <ArtifactsList artifacts={this.state.artifacts} collapsable={true} />
          </div>
        )}
        {this.state.testFailures.length !== 0 && (
          <div>
            <SectionHeading>Failing Tests</SectionHeading>
            <TestList
              testList={this.state.testFailures}
              params={this.props.params}
              collapsable={true}
            />
          </div>
        )}
        <div>
          <SectionHeading>Coverage</SectionHeading>
          <CoverageSummary coverage={this.state.diffCoverage} collapsable={true} />
        </div>
        <div>
          <SectionHeading>
            Jobs
            {failingJobs.length ? (
              <small> &mdash; {failingJobs.length} failed</small>
            ) : null}
          </SectionHeading>
          {unallowedFailures.length ? (
            <div>
              <JobList build={this.context.build} jobList={unallowedFailures} />
            </div>
          ) : null}
          {allowedFailures.length ? (
            <div>
              <SectionSubheading>Allowed Failures</SectionSubheading>
              <JobList build={this.context.build} jobList={allowedFailures} />
            </div>
          ) : null}
        </div>
      </Section>
    );
  }
}
