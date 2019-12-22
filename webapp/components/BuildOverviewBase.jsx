import React from 'react';
import PropTypes from 'prop-types';
import styled from '@emotion/styled';
import marked from 'marked';
import {sanitize} from 'dompurify';

import ArtifactsList from '../components/ArtifactsList';
import AsyncPage from '../components/AsyncPage';
import BundleList from '../components/BundleList';
import Button from '../components/Button';
import CoverageSummary from '../components/CoverageSummary';
import JobList from '../components/JobList';
import ObjectAuthor from '../components/ObjectAuthor';
import Section from '../components/Section';
import SectionHeading from '../components/SectionHeading';
import SectionSubheading from '../components/SectionSubheading';
import StyleViolationList from '../components/StyleViolationList';
import AggregateTestList from '../components/AggregateTestList';
import TimeSince from '../components/TimeSince';

const RevisionSection = styled(Section)`
  border: 2px solid #eee;
  padding: 10px;
`;

const RevisionSubject = styled.pre`
  margin-bottom: 10px;
  font-weight: bold;
  font-size: 0.8em;
`;

const RevisionMessage = styled.div`
  font-size: 0.8em;
  margin-bottom: 12px;

  h1,
  h2,
  h3,
  h4,
  h5,
  h6,
  p,
  ul,
  ol,
  blockquote,
  pre {
    margin-bottom: 10px;
  }

  h1 {
    font-size: 110%;
  }

  h2,
  h3 {
    font-size: 100%;
  }

  h4,
  h5,
  h6 {
    font-size: 90%;
  }
`;

const RevisionAuthor = styled.div`
  font-size: 0.8em;
  color: #666;

  img {
    display: inline-block;
    vertical-align: text-bottom;
    border-radius: 2px;
  }
`;

const RevisionSummary = ({repo, build}) => {
  let revision = build.revision;
  if (!revision) return null;
  let revisionBits = revision ? revision.message.split('\n') : [];
  let revisionSubject = revisionBits[0];
  let revisionMessage =
    revisionBits.length > 1
      ? revisionBits
          .slice(1)
          .join('\n')
          .replace(/^\s+|\s+$/g, '')
      : null;
  return (
    <RevisionSection>
      {repo.provider === 'gh' && revision && (
        <div style={{float: 'right'}}>
          <Button
            size="small"
            type="light"
            href={`https://github.com/${repo.owner_name}/${repo.name}/commit/${revision.sha}`}>
            View on GitHub
          </Button>
        </div>
      )}
      <RevisionSubject>{revisionSubject}</RevisionSubject>
      {revisionMessage && (
        <RevisionMessage
          dangerouslySetInnerHTML={{
            __html: sanitize(marked(revisionMessage))
          }}
        />
      )}
      <RevisionAuthor>
        <ObjectAuthor data={build} /> committed <TimeSince date={revision.committed_at} />
      </RevisionAuthor>
    </RevisionSection>
  );
};

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
      ['violationList', `${endpoint}/style-violations?allowed_failures=false`],
      ['testFailures', `${endpoint}/tests?result=failed&allowed_failures=false`],
      ['bundleStats', `${endpoint}/bundle-stats`],
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
    let {build, repo} = this.context;

    return (
      <div>
        <RevisionSummary repo={repo} build={build} />
        {!!this.state.testFailures.length && (
          <Section>
            <SectionHeading>Failing Tests</SectionHeading>
            <AggregateTestList
              build={build}
              repo={repo}
              testList={this.state.testFailures}
              params={this.props.params}
              collapsable={true}
            />
          </Section>
        )}
        {!!this.state.diffCoverage.length && (
          <Section>
            <SectionHeading>Coverage</SectionHeading>
            <CoverageSummary
              repo={repo}
              build={build}
              coverage={this.state.diffCoverage}
              collapsable={true}
            />
          </Section>
        )}
        {!!this.state.violationList.length && (
          <Section>
            <SectionHeading>Style Violations</SectionHeading>
            <StyleViolationList
              violationList={this.state.violationList}
              params={this.props.params}
              collapsable={true}
            />
          </Section>
        )}
        <Section>
          <SectionHeading>
            Jobs
            {!!failingJobs.length && <small> &mdash; {failingJobs.length} failed</small>}
          </SectionHeading>
          {!!unallowedFailures.length && (
            <div>
              <JobList build={this.context.build} jobList={unallowedFailures} />
            </div>
          )}
          {!!allowedFailures.length && (
            <div>
              <SectionSubheading>Allowed Failures</SectionSubheading>
              <JobList build={this.context.build} jobList={allowedFailures} />
            </div>
          )}
        </Section>
        {!!this.state.bundleStats.length && (
          <Section>
            <SectionHeading>Bundles</SectionHeading>
            <BundleList
              maxVisible={3}
              build={this.context.build}
              bundleList={this.state.bundleStats}
              collapsable={true}
            />
          </Section>
        )}
        {!!this.state.artifacts.length && (
          <Section>
            <SectionHeading>Artifacts</SectionHeading>
            <ArtifactsList
              maxVisible={5}
              build={this.context.build}
              artifacts={this.state.artifacts}
              collapsable={true}
            />
          </Section>
        )}
      </div>
    );
  }
}
