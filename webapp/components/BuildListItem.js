import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {Link} from 'react-router';
import moment from 'moment';
import styled, {css} from 'styled-components';
import {Flex, Box} from 'grid-styled';

import BuildDuration from './BuildDuration';
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
        <Flex align="center">
          <Box flex="1" width={6 / 12} pr={15}>
            <Flex>
              <Box width={15} mr={8}>
                <StatusIcon status={build.result}>
                  {build.result == 'passed' && <IconCircleCheck size="15" />}
                  {build.result == 'failed' && <IconCircleCross size="15" />}
                </StatusIcon>
              </Box>
              <Box flex="1" style={{minWidth: 0}}>
                <Message>
                  #{build.number} {build.source.revision.message}
                </Message>
                <Meta>
                  <Branch>branch-name</Branch>
                  <Commit>
                    {build.source.revision.sha.substr(0, 7)}
                  </Commit>
                </Meta>
              </Box>
            </Flex>
          </Box>
          <Box width={2 / 12}>
            <BuildDuration build={build} short={true} />
          </Box>
          <Box width={2 / 12}>
            {build.lineCoverageDiff >= 0
              ? `${parseInt(build.lineCoverageDiff * 100, 10)}%`
              : ''}
          </Box>
          <Box width={2 / 12}>
            author {moment(build.created_at).fromNow()}
          </Box>
        </Flex>
      </BuildListItemLink>
    );
  }
}

const BuildListItemLink = styled(Link)`
  display: block;
  padding: 10px 15px;
  color: #39364E;
  border-bottom: 1px solid #DBDAE3;
  font-size: 14px;

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

const Message = styled.div`
  font-size: 15px;
  line-height: 1.2;
  font-weight: 500;
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
  font-weight: 600;
`;

const Commit = styled(Branch)`
  font-weight: 400;
`;

const Meta = styled.div`
  display: flex;
  font-size: 12px;
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

export const StatusIcon = styled.div`
  ${props => {
    switch (props.status) {
      case 'passed':
        return css`
          svg {
            color: #76D392;
          }
        `;
      case 'failed':
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
