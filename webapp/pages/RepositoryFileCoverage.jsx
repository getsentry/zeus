import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import BuildCoverageComponent from '../components/BuildCoverage';

export default class RepositoryFileCoverage extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  getEndpoints() {
    let {repo} = this.context;
    return [
      [
        'result',
        `/repos/${repo.full_name}/file-coverage-tree`,
        {query: this.props.location.query}
      ]
    ];
  }

  renderBody() {
    return <BuildCoverageComponent result={this.state.result} {...this.props} />;
  }
}
