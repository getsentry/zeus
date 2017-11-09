import React from 'react';
import {Link} from 'react-router';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';

export default class RepositorySettings extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  renderBody() {
    let {repo} = this.context;
    return (
      <div>
        <ul>
          <li>
            <Link to={`/${repo.full_name}/settings/hooks`}>Hooks</Link>
          </li>
        </ul>
      </div>
    );
  }
}
