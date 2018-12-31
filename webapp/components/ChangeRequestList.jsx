import React, {Component} from 'react';
import PropTypes from 'prop-types';

import ChangeRequestListItem from '../components/ChangeRequestListItem';
import {ResultGrid, Column, Header} from '../components/ResultGrid';

export default class ChangeRequestList extends Component {
  static propTypes = {
    repo: PropTypes.object,
    changeRequestList: PropTypes.arrayOf(PropTypes.object).isRequired,
    columns: PropTypes.array,
    includeAuthor: PropTypes.bool,
    includeRepo: PropTypes.bool,
    params: PropTypes.object
  };

  static defaultProps = {
    columns: ['coverage', 'duration', 'date']
  };

  render() {
    let {
      changeRequestList,
      columns,
      includeAuthor,
      includeRepo,
      params,
      repo
    } = this.props;
    return (
      <ResultGrid>
        <Header>
          <Column>Change Request</Column>
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
            <Column width={120} textAlign="right" hide="sm">
              When
            </Column>
          )}
        </Header>
        <div>
          {changeRequestList.map(cr => {
            return (
              <ChangeRequestListItem
                key={cr.id}
                columns={columns}
                changeRequest={cr}
                params={params}
                repo={repo}
                includeAuthor={includeAuthor}
                includeRepo={includeRepo}
              />
            );
          })}
        </div>
      </ResultGrid>
    );
  }
}
