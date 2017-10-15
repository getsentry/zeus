import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {Flex, Box} from 'grid-styled';

import RevisionListItem from '../components/RevisionListItem';
import Panel from '../components/Panel';
import ResultGridHeader from '../components/ResultGridHeader';

export default class RevisionList extends Component {
  static propTypes = {
    revisionList: PropTypes.arrayOf(PropTypes.object).isRequired,
    repo: PropTypes.object
  };

  render() {
    let {revisionList, repo, params} = this.props;
    return (
      <Panel>
        <ResultGridHeader>
          <Flex>
            <Box flex="1" width={6 / 12} pr={15}>
              Revision
            </Box>
            <Box width={2 / 12} style={{textAlign: 'right'}}>
              When
            </Box>
          </Flex>
        </ResultGridHeader>
        <div>
          {revisionList.map(revision => {
            return (
              <RevisionListItem
                key={revision.sha}
                repo={repo}
                revision={revision}
                params={params}
              />
            );
          })}
        </div>
      </Panel>
    );
  }
}
