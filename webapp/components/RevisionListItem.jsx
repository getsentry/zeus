import React, {Component} from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import {Flex, Box} from 'grid-styled';

import BuildListItem from './BuildListItem';
import ListItemLink from './ListItemLink';
import ObjectAuthor from './ObjectAuthor';
import {Column, Row} from './ResultGrid';
import TimeSince from './TimeSince';

export default class RevisionListItem extends Component {
  static propTypes = {
    repo: PropTypes.object,
    revision: PropTypes.object.isRequired,
    includeAuthor: PropTypes.bool,
    includeRepo: PropTypes.bool
  };

  static defaultProps = {
    includeAuthor: true
  };

  render() {
    let {includeAuthor, includeRepo, revision} = this.props;
    let repo = revision.repository || this.props.repo;
    if (revision.latest_build)
      return (
        <BuildListItem
          build={revision.latest_build}
          repo={repo}
          date={revision.committed_at || revision.created_at}
        />
      );

    return (
      <ListItemLink to={null}>
        <Row>
          <Column>
            <Flex>
              <Box width={15} mr={8} />
              <Box flex="1" style={{minWidth: 0}}>
                <Message>
                  {revision.message.split('\n')[0]}
                </Message>
                <Meta>
                  {includeRepo
                    ? <RepoLink to={`/${repo.full_name}`}>
                        {repo.owner_name}/{repo.name}
                      </RepoLink>
                    : null}
                  <Commit>
                    {revision.sha.substr(0, 7)}
                  </Commit>
                  {includeAuthor
                    ? <Author>
                        <ObjectAuthor data={revision} />
                      </Author>
                    : null}
                </Meta>
              </Box>
            </Flex>
          </Column>
          <Column width={90} textAlign="center" />
          <Column width={90} textAlign="center" />
          <Column width={150} textAlign="right">
            <TimeSince date={revision.committed_at || revision.created_at} />
          </Column>
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
