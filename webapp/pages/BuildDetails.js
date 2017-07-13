import React from 'react';
import PropTypes from 'prop-types';
import styled, {css} from 'styled-components';

import AsyncPage from '../components/AsyncPage';
import {Breadcrumbs, Crumb, CrumbLink} from '../components/Breadcrumbs';
import BuildAuthor from '../components/BuildAuthor';
import ObjectDuration from '../components/ObjectDuration';
import TabbedNavItem from '../components/TabbedNavItem';
import TimeSince from '../components/TimeSince';

import IconCircleCheck from '../assets/IconCircleCheck';
import IconCircleCross from '../assets/IconCircleCross';
import IconClock from '../assets/IconClock';

export default class BuildDetails extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  static childContextTypes = {
    ...AsyncPage.childContextTypes,
    ...BuildDetails.contextTypes,
    build: PropTypes.object.isRequired
  };

  getChildContext() {
    return {
      ...this.context,
      build: this.state.build
    };
  }

  getEndpoints() {
    let {buildNumber, repoName} = this.props.params;
    return [['build', `/repos/${repoName}/builds/${buildNumber}`]];
  }

  getTitle() {
    return 'Build Details';
  }

  render() {
    // happens before loading is done
    let {build} = this.state;
    let {repoName} = this.props.params;
    return (
      <div>
        <Breadcrumbs>
          <CrumbLink to={`/repos/${repoName}/builds`}>
            {repoName}
          </CrumbLink>
          {build &&
            <Crumb active={true}>
              #{build.number}
            </Crumb>}
        </Breadcrumbs>
        {this.renderContent()}
      </div>
    );
  }

  renderBody() {
    let {build} = this.state;
    let {buildNumber, repoName} = this.props.params;
    return (
      <div>
        <BuildSummary>
          <Header>
            <Message>
              {build.source.revision.message}
            </Message>
          </Header>
          <Meta>
            {build.status === 'finished' &&
              <DurationWrapper result={build.result}>
                {build.result == 'passed' && <IconCircleCheck size="15" />}
                {build.result == 'failed' && <IconCircleCross size="15" />}
                {build.status} <TimeSince date={build.finished_at} /> in{' '}
                <ObjectDuration data={build} short={true} />
              </DurationWrapper>}
            <Time>
              <IconClock size="15" />
              {build.status === 'queued'
                ? <span>
                    created <TimeSince date={build.created_at} />
                  </span>
                : <span>
                    started <TimeSince date={build.started_at} />
                  </span>}
            </Time>
            <Author>
              <BuildAuthor build={build} />
            </Author>
            <Commit>
              {build.source.revision.sha.substr(0, 7)}
            </Commit>
          </Meta>
          <Tabs>
            <TabbedNavItem
              to={`/repos/${repoName}/builds/${buildNumber}`}
              onlyActiveOnIndex={true}>
              Overview
            </TabbedNavItem>
            <TabbedNavItem to={`/repos/${repoName}/builds/${buildNumber}/tests`}>
              Tests
            </TabbedNavItem>
            <TabbedNavItem to={`/repos/${repoName}/builds/${buildNumber}/coverage`}>
              Code Coverage
            </TabbedNavItem>
          </Tabs>
        </BuildSummary>
        {this.props.children}
      </div>
    );
  }
}

const Section = styled.div`padding: 20px;`;

const BuildSummary = styled(Section)`
  padding-top: 15px;
  padding-bottom: 0;
  box-shadow: inset 0 -1px 0 #E0E4E8;
`;

const Tabs = styled.div`
  margin-top: 5px;
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

const Branch = styled.div`font-family: "Monaco", monospace;`;

const Meta = styled.div`
  display: flex;
  align-items: center;
  margin-top: 5px;
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
      case 'pass':
        return css`
          svg {
            color: #76D392;
          }
        `;
      case 'fail':
        return css`
          color: #F06E5B;
          svg {
            color: #F06E5B;
          }
        `;
      default:
        return css`
          svg {
            color: #BFBFCB;
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
