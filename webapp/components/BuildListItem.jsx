import React, {Component} from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import {Flex, Box} from 'grid-styled';

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
    date: PropTypes.object,
    includeAuthor: PropTypes.bool,
    includeRepo: PropTypes.bool
  };

  static defaultProps = {
    includeAuthor: true
  };

  render() {
    let {build, includeAuthor, includeRepo} = this.props;
    let repo = this.props.repo || build.repository;
    let link = build.number
      ? `/${repo.full_name}/builds/${build.number}`
      : `/${repo.full_name}/revisions/${build.source.revision.sha}`;
    return (
      <ListItemLink to={link}>
        <Row>
          <Column>
            <Flex>
              <Box width={15} mr={8}>
                <ObjectResult data={build} />
              </Box>
              <Box flex="1" style={{minWidth: 0}}>
                <Message>
                  {build.label || build.source.revision.message.split('\n')[0]}
                </Message>
                <Meta>
                  {includeRepo
                    ? <RepoLink to={`/${repo.full_name}`}>
                        {build.repository.owner_name}/{build.repository.name}
                      </RepoLink>
                    : null}
                  <Commit>
                    {build.source.revision.sha.substr(0, 7)}
                  </Commit>
                  {includeAuthor
                    ? <Author>
                        <ObjectAuthor data={build} />
                      </Author>
                    : null}
                </Meta>
              </Box>
            </Flex>
          </Column>
          <Column width={90} textAlign="center">
            <ObjectCoverage data={build} />
          </Column>
          <Column width={90} textAlign="center">
            <ObjectDuration data={build} short={true} />
          </Column>
          <Column width={150} textAlign="right">
            <TimeSince date={this.props.date || build.created_at} />
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
