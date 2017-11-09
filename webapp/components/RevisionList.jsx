import React, {Component} from 'react';
import PropTypes from 'prop-types';

import RevisionListItem from '../components/RevisionListItem';
import {ResultGrid, Column, Header} from '../components/ResultGrid';

export default class RevisionList extends Component {
  static propTypes = {
    revisionList: PropTypes.arrayOf(PropTypes.object).isRequired,
    repo: PropTypes.object
  };

  render() {
    let {revisionList, repo, params} = this.props;
    return (
      <ResultGrid>
        <Header>
          <Column>Revision</Column>
          <Column width={90} textAlign="center">
            Coverage
          </Column>
          <Column width={90} textAlign="center">
            Duration
          </Column>
          <Column width={150} textAlign="right">
            Commit Date
          </Column>
        </Header>
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
      </ResultGrid>
    );
  }
}
