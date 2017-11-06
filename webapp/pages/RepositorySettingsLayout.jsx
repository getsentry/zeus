import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import RepositoryContent from '../components/RepositoryContent';
import RepositoryHeader from '../components/RepositoryHeader';

export default class RepositorySettingsLayout extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  renderBody() {
    return (
      <div>
        <RepositoryHeader />
        <RepositoryContent {...this.props}>
          {this.props.children}
        </RepositoryContent>
      </div>
    );
  }
}
