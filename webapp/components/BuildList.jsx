import React, {Component} from 'react';
import PropTypes from 'prop-types';

import BuildListItem from '../components/BuildListItem';
import {ResultGrid, Column, Header} from '../components/ResultGrid';

export default class BuildList extends Component {
  static propTypes = {
    repo: PropTypes.object,
    buildList: PropTypes.arrayOf(PropTypes.object).isRequired,
    columns: PropTypes.array,
    includeAuthor: PropTypes.bool,
    includeRepo: PropTypes.bool
  };

  static defaultProps = {
    columns: ['coverage', 'duration', 'date']
  };

  render() {
    let {buildList, columns, includeAuthor, includeRepo, params, repo} = this.props;
    return (
      <ResultGrid>
        <Header>
          <Column>Build</Column>
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
          {buildList.map(build => {
            return (
              <BuildListItem
                key={build.id}
                columns={columns}
                build={build}
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
