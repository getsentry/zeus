import React, {Component} from 'react';
import {Link} from 'react-router';
import styled, {css} from 'styled-components';

import IconCircleCheck from '../assets/IconCircleCheck';
import IconCircleCross from '../assets/IconCircleCross';
import IconClock from '../assets/IconClock';

export default class BuildListItem extends Component {
  render() {
    const {message, status, duration, timestamp, author, branch, commit, slug} = {...this.props};
    return (
      <BuildListItemLink to={slug}>
        <Header>
          <Message>{message}</Message>
          <Branch>{branch}</Branch>
        </Header>
        <Meta>
          <Duration status={status}>
            {status == "pass" &&
              <IconCircleCheck size="15" />
            }
            {status == "fail" &&
              <IconCircleCross size="15" />
            }
            {duration}
          </Duration>
          <Time>
            <IconClock size="15" />{author} {timestamp}
          </Time>
          <Commit>{commit}</Commit>
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

  &.${(props) => props.activeClassName} {
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
  activeClassName: 'active',
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

const Branch = styled.div`
  font-family: "Monaco", monospace;
  font-size: 12px;
`;

const Meta = styled.div`
  display: flex;
  font-size: 12px;
  margin-top: 5px;
  color: #7F7D8F;

  > div {
    margin-right: 12px;

    &:last-child {
      margin-right: 0;
    }
  }

  svg {
    vertical-align: bottom !important;
    margin-right: 5px;
    color: #BFBFCB;
  }
`;

const Duration = styled.div`
  color: ${(props) => (props.status == "fail") ? '#F06E5B' : 'inherit'};

  svg {
    color: ${(props) => (props.status == "fail") ? '#F06E5B' : '#BFBFCB'};
  }
`;

const Time = styled.div`

`;

const Commit = styled(Branch)`
  flex: 1;
  text-align: right;
`;
