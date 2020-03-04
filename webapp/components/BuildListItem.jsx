import React, {Component} from 'react';
import PropTypes from 'prop-types';
import styled from '@emotion/styled';
import {Flex, Box} from '@rebass/grid/emotion';

import ListItemLink from './ListItemLink';
import ObjectAuthor from './ObjectAuthor';
import ObjectCoverage from './ObjectCoverage';
import ObjectDuration from './ObjectDuration';
import ObjectResult from './ObjectResult';
import {Column, Row} from './ResultGrid';
import TimeSince from './TimeSince';

export default class BuildListItem extends Component {
  static propTypes = {
    build: PropTypes.object.isRequired,
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

  static contextTypes = {
    router: PropTypes.object.isRequired
  };

  render() {
    let {build, columns, includeAuthor, includeRepo} = this.props;
    let repo = this.props.repo || build.repository;
    let link = build
      ? build.number
        ? `/${repo.full_name}/builds/${build.number}`
        : build.revision
        ? `/${repo.full_name}/revisions/${build.revision.sha}`
        : null
      : null;
    return (
      <ListItemLink to={link}>
        <Row>
          <Column>
            <Flex>
              <Box width={15} mr={2}>
                <ObjectResult data={build} />
              </Box>
              <Box flex="1" style={{minWidth: 0}}>
                <Message>{build.label}</Message>
                <Meta>
                  {includeRepo ? (
                    <RepoLink to={`/${repo.full_name}`}>
                      {repo.owner_name}/{repo.name}
                    </RepoLink>
                  ) : null}
                  <Commit>
                    {build.revision ? build.revision.sha.substr(0, 7) : build.ref}
                  </Commit>
                  {includeAuthor ? (
                    <Author>
                      <ObjectAuthor data={build} />
                    </Author>
                  ) : null}
                </Meta>
              </Box>
            </Flex>
          </Column>
          {columns.indexOf('coverage') !== -1 && (
            <Column width={90} textAlign="center" hide="sm">
              <ObjectCoverage data={build} />
            </Column>
          )}
          {columns.indexOf('duration') !== -1 && (
            <Column width={90} textAlign="center" hide="sm">
              <ObjectDuration data={build} short={true} />
            </Column>
          )}
          {columns.indexOf('date') !== -1 && (
            <Column width={120} textAlign="right" hide="sm">
              <TimeSince date={this.props.date || build.created_at} />
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
