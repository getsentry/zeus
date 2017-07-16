import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import {Breadcrumbs, Crumb} from '../components/Breadcrumbs';
import ScrollView from '../components/ScrollView';

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
          <Crumb active={true}>
            {repo.name}
          </Crumb>
        </Breadcrumbs>
        <ScrollView>
          <RepositoryTestListBody {...this.props} />
        </ScrollView>
      </div>
    );
  }
}

class RepositoryTestListBody extends AsyncPage {
  getEndpoints() {
    let {repoName} = this.props.params;
    return [['testList', `/repos/${repoName}/tests`]];
  }

  renderBody() {
    return (
      <ul>
        {this.state.testList.map(test => {
          return (
            <li key={test.name}>
              {test.name}
            </li>
          );
        })}
      </ul>
    );
  }
}
