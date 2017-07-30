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

  renderBody() {
    // let repo = this.context.repo;
    // let basePath = `/${repo.owner_name}/${repo.name}`;
    return (
      <div>
        <RepositoryHeader />
        <RepositoryContent {...this.props}>Put settings here!</RepositoryContent>
      </div>
    );
  }
}
