import React from 'react';
import PropTypes from 'prop-types';
import styled, {css} from 'styled-components';

import AsyncPage from '../components/AsyncPage';
import Badge from '../components/Badge';
import ObjectAuthor from '../components/ObjectAuthor';
import {Breadcrumbs, Crumb, CrumbLink} from '../components/Breadcrumbs';
import ObjectCoverage from '../components/ObjectCoverage';
import ObjectDuration from '../components/ObjectDuration';
import ObjectResult from '../components/ObjectResult';
import RepositoryHeader from '../components/RepositoryHeader';
import ScrollView from '../components/ScrollView';
import TabbedNavItem from '../components/TabbedNavItem';
import TimeSince from '../components/TimeSince';

import IconClock from '../assets/IconClock';

export default class BuildDetails extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  static childContextTypes = {
    ...AsyncPage.childContextTypes,
    ...BuildDetails.contextTypes,
    build: PropTypes.object
  };

  getChildContext() {
    return {
      ...this.context,
      build: this.state.build
    };
  }

  getEndpoints() {
    let {repo} = this.context;
    let {buildNumber} = this.props.params;
    return [['build', `/repos/${repo.full_name}/builds/${buildNumber}`]];
  }

  getTitle() {
    return 'Build Details';
  }

  getHeaderMessage() {
    const {build} = this.state;
    const {message} = build.source.revision;

    // Extract the first line only, if there are multiple lines
    const match = (build.label || message).match(/.*(?=\n|$)/);
    return match && match[0];
  }

  shouldFetchUpdates() {
    return (this.state.build || {}).status !== 'finished';
  }

  render() {
    // happens before loading is done
    let {repo} = this.context;
    let {buildNumber} = this.props.params;
    return (
      <RepositoryHeader>
        <Breadcrumbs>
          <CrumbLink to={`/${repo.provider}/${repo.owner_name}`}>
            {repo.owner_name}
          </CrumbLink>
          <CrumbLink to={`/${repo.full_name}`}>{repo.name}</CrumbLink>
          <Crumb>#{buildNumber}</Crumb>
        </Breadcrumbs>
        <ScrollView>{this.renderContent()}</ScrollView>
      </RepositoryHeader>
    );
  }

  renderBody() {
    let {build} = this.state;
    let {repo} = this.context;
    let {buildNumber} = this.props.params;
    let hasCoverage =
      build.stats.coverage.lines_covered > 0 || build.stats.coverage.lines_uncovered > 0;
    let hasTests = build.stats.tests.count > 0;
    return (
      <div>
        <BuildSummary>
          <Header>
            <Message>{this.getHeaderMessage()}</Message>
          </Header>
          <Meta>
            {build.status === 'finished' && (
              <DurationWrapper result={build.result}>
                <ObjectResult data={build} />
                {build.result} <TimeSince date={build.finished_at} /> in{' '}
                <ObjectDuration data={build} short={true} />
              </DurationWrapper>
            )}
            <Time>
              <IconClock size="15" />
              {build.status === 'queued' ? (
                <span>
                  created <TimeSince date={build.created_at} />
                </span>
              ) : (
                <span>
                  started <TimeSince date={build.started_at} />
                </span>
              )}
            </Time>
            <Author>
              <ObjectAuthor data={build} />
            </Author>
            <Commit>{build.source.revision.sha.substr(0, 7)}</Commit>
          </Meta>
          <Tabs>
            <TabbedNavItem
              to={`/${repo.full_name}/builds/${buildNumber}`}
              onlyActiveOnIndex={true}>
              Overview
            </TabbedNavItem>
            <TabbedNavItem
              to={`/${repo.full_name}/builds/${buildNumber}/tests`}
              disabled={!hasTests}>
              Tests
              {hasTests ? (
                <Badge>{build.stats.tests.count.toLocaleString()}</Badge>
              ) : null}
            </TabbedNavItem>
            <TabbedNavItem
              to={`/${repo.full_name}/builds/${buildNumber}/coverage`}
              disabled={!hasCoverage}>
              Code Coverage
              {hasCoverage ? (
                <Badge>
                  <ObjectCoverage data={build} diff={false} />
                </Badge>
              ) : null}
            </TabbedNavItem>
            <TabbedNavItem to={`/${repo.full_name}/builds/${buildNumber}/diff`}>
              Diff
            </TabbedNavItem>
            <TabbedNavItem to={`/${repo.full_name}/builds/${buildNumber}/artifacts`}>
              Artifacts
            </TabbedNavItem>
          </Tabs>
        </BuildSummary>
        {this.props.children}
      </div>
    );
  }
}

const Section = styled.div`
  padding: 20px;
`;

const BuildSummary = styled(Section)`
  padding-bottom: 0;
  padding-top: 0;
  box-shadow: inset 0 -1px 0 #e0e4e8;
`;

const Tabs = styled.div`
  margin-bottom: 20px;
  overflow: hidden;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 4px;
`;

const Message = styled.div`
  font-size: 24px;
  font-weight: 500;
  flex: 1;
  padding-right: 5px;
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow: hidden;
`;

const Branch = styled.div`
  font-family: 'Monaco', monospace;
`;

const Meta = styled.div`
  display: flex;
  align-items: center;
  margin-top: 5px;
  margin-bottom: 15px;
  color: #7f7d8f;
  font-size: 14px;

  > div {
    margin-right: 20px;

    &:last-child {
      margin-right: 0;
    }
  }

  svg {
    margin-right: 6px;
    color: #bfbfcb;
    position: relative;
    top: -1px;
  }
`;

export const DurationWrapper = styled.div`
  ${props => {
    switch (props.result) {
      case 'passed':
        return css`
          svg {
            color: #76d392;
          }
        `;
      case 'failed':
        return css`
          color: #f06e5b;
          svg {
            color: #f06e5b;
          }
        `;
      default:
        return css`
          svg {
            color: #bfbfcb;
          }
        `;
    }
  }};
`;

const Time = styled.div``;

const Author = styled.div``;

const Commit = styled(Branch)`
  flex: 1;
  text-align: right;
`;
