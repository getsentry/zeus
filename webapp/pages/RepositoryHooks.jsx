import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import RepositoryContent from '../components/RepositoryContent';
import RepositoryHeader from '../components/RepositoryHeader';

export default class RepositorySettings extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  getEndpoints() {
    let repo = this.context.repo;
    return [['hookList', `/repos/${repo.full_name}/hooks`]];
  }

  renderBody() {
    // let repo = this.context.repo;
    // let basePath = `/${repo.full_name}`;
    return (
      <div>
        <RepositoryHeader />
        <RepositoryContent {...this.props}>
          <h2>Hooks</h2>
          <ul>
            {this.state.hookList.map(hook => {
              return (
                <li key={hook.id}>
                  {hook.id}
                </li>
              );
            })}
          </ul>
        </RepositoryContent>
      </div>
    );
  }
}
