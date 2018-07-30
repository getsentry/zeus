import React, {Component} from 'react';
import PropTypes from 'prop-types';

import RevisionListItem from '../components/RevisionListItem';
import {ResultGrid, Column, Header} from '../components/ResultGrid';

export default class RevisionList extends Component {
  static propTypes = {
    revisionList: PropTypes.arrayOf(PropTypes.object).isRequired,
    repo: PropTypes.object,
    columns: PropTypes.array,
    params: PropTypes.object
  };

  static defaultProps = {
    columns: ['coverage', 'duration', 'date']
  };

  render() {
    let {columns, revisionList, repo, params} = this.props;
    return (
      <ResultGrid>
        <Header>
          <Column>Revision</Column>
          {columns.indexOf('coverage') !== -1 && (
            <Column width={90} textAlign="center" hide="sm">
              Coverage
            </Column>
          )}
          {columns.indexOf('duration') !== -1 && (
            <Column width={90} textAlign="center" hide="sm">
              Duration
            </Column>
          )}
          {columns.indexOf('date') !== -1 && (
            <Column width={150} textAlign="right" hide="sm">
              Commit Date
            </Column>
          )}
        </Header>
        <div>
          {revisionList.map(revision => {
            return (
              <RevisionListItem
                key={revision.sha}
                repo={repo}
                revision={revision}
                params={params}
                columns={columns}
              />
            );
          })}
        </div>
      </ResultGrid>
    );
  }
}
