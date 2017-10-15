import React, {Component} from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import {Flex, Box} from 'grid-styled';

import ListItemLink from './ListItemLink';
import ObjectAuthor from './ObjectAuthor';
import ObjectResult from './ObjectResult';
import ResultGridRow from './ResultGridRow';

export default class RevisionListItem extends Component {
  static propTypes = {
    revision: PropTypes.object.isRequired,
    repo: PropTypes.object
  };

  render() {
    let {revision} = this.props;
    let repo = revision.repository || this.props.repo;
    return (
      <ListItemLink
        to={
          revision.latest_build
            ? `/${repo.full_name}/builds/${revision.latest_build.number}`
            : null
        }>
        <ResultGridRow>
          <Flex align="center">
            <Box flex="1" width={8 / 12} pr={15}>
              <div>
                <Message>
                  {revision.sha.substr(0, 7)} {revision.message.split('\n')[0]}
                </Message>
              </div>
              {revision.latest_build
                ? <Meta>
                    <Flex>
                      <Box width={15} mr={8}>
                        <ObjectResult data={revision.latest_build} />
                      </Box>
                      <Box flex="1" style={{minWidth: 0}}>
                        <Message>
                          #{revision.latest_build.number}{' '}
                          {revision.latest_build.label || ''}
                        </Message>
                        <Meta>
                          <Author>
                            <ObjectAuthor data={revision.latest_build} />
                          </Author>
                        </Meta>
                      </Box>
                    </Flex>
                  </Meta>
                : null}
            </Box>
          </Flex>
        </ResultGridRow>
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
  font-family: "Monaco", monospace;
  font-size: 12px;
  font-weight: 600;
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
