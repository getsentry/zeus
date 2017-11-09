import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';

export default class RepositorySettingsLayout extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  renderBody() {
    return (
      <div>
        {this.props.children}
      </div>
    );
  }
}
