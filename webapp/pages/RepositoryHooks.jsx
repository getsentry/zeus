import React from 'react';
import {Link} from 'react-router';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';

export default class RepositoryHooks extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  getEndpoints() {
    let repo = this.context.repo;
    return [['hookList', `/repos/${repo.full_name}/hooks`]];
  }

  renderBody() {
    let repo = this.context.repo;
    return (
      <div>
        <h2>Hooks</h2>
        <ul>
          {this.state.hookList.map(hook => {
            return (
              <li key={hook.id}>
                <Link to={`/${repo.full_name}/settings/hooks/${hook.id}`}>
                  {hook.id}
                </Link>
              </li>
            );
          })}
        </ul>
      </div>
    );
  }
}
