import React from 'react';
import PropTypes from 'prop-types';
import moment from 'moment';
import styled, {css} from 'styled-components';

import AsyncComponent from '../components/AsyncComponent';
import BuildDuration from '../components/BuildDuration';
import {HeaderLink, HorizontalHeader} from '../components/HorizontalHeader';
import TabbedNavItem from '../components/TabbedNavItem';

import IconCircleCheck from '../assets/IconCircleCheck';
import IconCircleCross from '../assets/IconCircleCross';
import IconClock from '../assets/IconClock';

export default class BuildDetails extends AsyncComponent {
  static contextTypes = {
    ...AsyncComponent.contextTypes,
    repo: PropTypes.object.isRequired
  };

  static childContextTypes = {
    ...AsyncComponent.childContextTypes,
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

  renderBody() {
    let {repo} = this.context;
    let {build} = this.state;
    let {buildNumber, repoName} = this.props.params;
    return (
      <div>
        <HorizontalHeader>
          <HeaderLink to={`/repos/${repo.name}`}>
            {repo.name}
          </HeaderLink>
        </HorizontalHeader>
        <BuildSummary>
          <Header>
            <Message>
              {build.source.revision.message}
            </Message>
            <Branch>branch-name</Branch>
          </Header>
          <Meta>
            {build.status === 'finished' &&
              <DurationWrapper result={build.result}>
                {build.result == 'passed' && <IconCircleCheck size="15" />}
                {build.result == 'failed' && <IconCircleCross size="15" />}
                {build.status} {moment(build.finished_at).fromNow()} in{' '}
                <BuildDuration build={build} short={true} />
              </DurationWrapper>}
            <Time>
              <IconClock size="15" />
              {build.status === 'queued'
                ? <span>
                    created {moment(build.created_at).fromNow()}
                  </span>
                : <span>
                    started {moment(build.started_at).fromNow()}
                  </span>}
            </Time>
            <Commit>
              {build.source.revision.sha.substr(0, 7)}
            </Commit>
          </Meta>
          <Tabs>
            <TabbedNavItem
              to={`/repos/${repoName}/builds/${buildNumber}`}
              onlyActiveOnIndex={true}>
              Jobs
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

const Section = styled.div`padding: 30px;`;

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

const Commit = styled(Branch)`
  flex: 1;
  text-align: right;
`;
