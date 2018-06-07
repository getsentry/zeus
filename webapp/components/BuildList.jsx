import React, {Component} from 'react';
import PropTypes from 'prop-types';

import BuildListItem from '../components/BuildListItem';
import {ResultGrid, Column, Header} from '../components/ResultGrid';

export default class BuildList extends Component {
  static propTypes = {
    repo: PropTypes.object,
    buildList: PropTypes.arrayOf(PropTypes.object).isRequired,
    includeAuthor: PropTypes.bool,
    includeRepo: PropTypes.bool
  };

  render() {
    let {buildList, includeAuthor, includeRepo, params, repo} = this.props;
    return (
      <ResultGrid>
        <Header>
          <Column>Build</Column>
          <Column width={90} textAlign="center" hide="sm">
            Coverage
          </Column>
          <Column width={90} textAlign="center" hide="sm">
            Duration
          </Column>
          <Column width={150} textAlign="right" hide="sm">
            When
          </Column>
        </Header>
        <div>
          {buildList.map(build => {
            return (
              <BuildListItem
                key={build.id}
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
