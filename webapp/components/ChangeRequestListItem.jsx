import React, {Component} from 'react';
import PropTypes from 'prop-types';
import styled from '@emotion/styled';
import {Flex, Box} from '@rebass/grid/emotion';

import BuildListItem from './BuildListItem';
import ListItemLink from './ListItemLink';
import ObjectAuthor from './ObjectAuthor';
import {Column, Row} from './ResultGrid';
import TimeSince from './TimeSince';

export default class ChangeRequestListItem extends Component {
  static propTypes = {
    changeRequest: PropTypes.object.isRequired,
    repo: PropTypes.object,
    date: PropTypes.any,
    includeAuthor: PropTypes.bool,
    includeRepo: PropTypes.bool,
    columns: PropTypes.array
  };

  static defaultProps = {
    includeAuthor: true,
    columns: ['coverage', 'duration', 'date']
  };

  render() {
    let {changeRequest, columns, includeAuthor, includeRepo} = this.props;
    let repo = this.props.repo || changeRequest.repository;

    // TODO(dcramer):
    // let link = changeRequest.number
    //   ? `/${repo.full_name}/change-requests/${changeRequest.number}`
    //   : `/${repo.full_name}/revisions/${changeRequest.head_revision.sha}`;

    let link = `/${repo.full_name}/revisions/${changeRequest.head_revision.sha}`;

    if (changeRequest.latest_build)
      return (
        <BuildListItem
          build={changeRequest.latest_build}
          repo={repo}
          date={changeRequest.committed_at || changeRequest.created_at}
          columns={columns}
        />
      );

    return (
      <ListItemLink to={link}>
        <Row>
          <Column>
            <Flex>
              <Box width={15} mr={2} />
              <Box flex="1" style={{minWidth: 0}}>
                <Message>{changeRequest.message.split('\n')[0]}</Message>
                <Meta>
                  {includeRepo ? (
                    <RepoLink to={`/${repo.full_name}`}>
                      {repo.owner_name}/{repo.name}
                    </RepoLink>
                  ) : null}
                  <Commit>{changeRequest.head_revision.sha.substr(0, 7)}</Commit>
                  {includeAuthor ? (
                    <Author>
                      <ObjectAuthor data={changeRequest} />
                    </Author>
                  ) : null}
                </Meta>
              </Box>
            </Flex>
          </Column>
          {columns.indexOf('coverage') !== -1 && (
            <Column width={90} textAlign="center" hide="sm" />
          )}
          {columns.indexOf('duration') !== -1 && (
            <Column width={90} textAlign="center" hide="sm" />
          )}
          {columns.indexOf('date') !== -1 && (
            <Column width={120} textAlign="right" hide="sm">
              <TimeSince date={this.props.date || changeRequest.created_at} />
            </Column>
          )}
        </Row>
      </ListItemLink>
    );
  }
}

const Message = styled.div`
  font-size: 15px;
  line-height: 1.2;
  font-weight: 500;
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow: hidden;
`;

const Author = styled.div`
  font-family: 'Monaco', monospace;
  font-size: 12px;
  font-weight: 600;
`;

const Commit = styled(Author)`
  font-weight: 400;
`;

const RepoLink = styled(Author)`
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
