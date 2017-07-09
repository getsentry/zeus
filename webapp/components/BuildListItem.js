import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {Link} from 'react-router';
import moment from 'moment';
import styled, {css} from 'styled-components';

import IconCircleCheck from '../assets/IconCircleCheck';
import IconCircleCross from '../assets/IconCircleCross';
import IconClock from '../assets/IconClock';

export default class BuildListItem extends Component {
  static contextTypes = {
    repo: PropTypes.object.isRequired
  };

  static propTypes = {
    build: PropTypes.object.isRequired
  };

  render() {
    let {repo} = this.context;
    let {build} = this.props;
    return (
      <BuildListItemLink to={`/repos/${repo.name}/builds/${build.number}`}>
        <Header>
          <span style={{marginRight: 10}}>
            #{build.number}
          </span>
          <Message>
            {build.source.revision.message}
          </Message>
          <TestCount>
            {build.testCount || ''}
          </TestCount>
          <Coverage>
            {build.lineCoverageDiff >= 0
              ? `${parseInt(build.lineCoverageDiff * 100, 10)}%`
              : ''}
          </Coverage>
          <Branch>branch-name</Branch>
        </Header>
        <Meta>
          <DurationWrapper result={build.result}>
            {build.result == 'passed' && <IconCircleCheck size="15" />}
            {build.result == 'failed' && <IconCircleCross size="15" />}
            {build.status == 'finished' && moment(build.created_at).fromNow()}
          </DurationWrapper>
          <Time>
            <IconClock size="15" />
            author {moment(build.created_at).fromNow()}
          </Time>
          <Commit>
            {build.source.revision.sha.substr(0, 7)}
          </Commit>
        </Meta>
      </BuildListItemLink>
    );
  }
}

const BuildListItemLink = styled(Link)`
  display: block;
  padding: 15px 20px;
  color: #39364E;
  border-bottom: 1px solid #DBDAE3;

  &:hover {
    background-color: #F0EFF5;
  }

  &.${props => props.activeClassName} {
    color: #fff;
    background: #7B6BE6;

    > div {
      color: #fff !important;

      svg {
        color: #fff;
        opacity: .5;
      }
    }
  }
`;

BuildListItemLink.defaultProps = {
  activeClassName: 'active'
};

const Header = styled.div`
  display: flex;
  font-size: 14px;
`;

const Message = styled.div`
  font-weight: 500;
  flex: 1;
  padding-right: 5px;
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow: hidden;
`;

const TestCount = styled.div`
  flex: 1;
  font-family: "Monaco", monospace;
  font-size: 12px;
`;

const Coverage = styled.div`
  flex: 1;
  font-family: "Monaco", monospace;
  font-size: 12px;
`;

const Branch = styled.div`
  font-family: "Monaco", monospace;
  font-size: 12px;
`;

const Meta = styled.div`
  display: flex;
  font-size: 12px;
  margin-top: 5px;
  color: #7f7d8f;

  > div {
    margin-right: 12px;

    &:last-child {
      margin-right: 0;
    }
  }

  svg {
    vertical-align: bottom !important;
    margin-right: 5px;
    color: #bfbfcb;
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
