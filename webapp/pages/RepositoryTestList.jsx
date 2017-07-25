import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import {Breadcrumbs, Crumb} from '../components/Breadcrumbs';
import RepositoryContent from '../components/RepositoryContent';
import TestList from '../components/TestList';

export default class RepositoryTestList extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  getTitle() {
    return this.context.repo.name;
  }

  renderBody() {
    let {repo} = this.context;
    return (
      <div>
        <Breadcrumbs>
          <Crumb>
            {repo.owner_name}
          </Crumb>
          <Crumb>
            {repo.name}
          </Crumb>
        </Breadcrumbs>
        <RepositoryContent {...this.props}>
          <RepositoryTestListBody {...this.props} />
        </RepositoryContent>
      </div>
    );
  }
}

class RepositoryTestListBody extends AsyncPage {
  getEndpoints() {
    let {ownerName, repoName} = this.props.params;
    return [['testList', `/repos/${ownerName}/${repoName}/tests`]];
  }

  renderBody() {
    return <TestList testList={this.state.testList} />;
  }
}
