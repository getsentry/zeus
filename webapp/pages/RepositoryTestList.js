import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import {Breadcrumbs, Crumb} from '../components/Breadcrumbs';
import ScrollView from '../components/ScrollView';

export default class ProjectTestList extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    project: PropTypes.object.isRequired
  };

  getTitle() {
    return this.context.project.name;
  }

  renderBody() {
    let {project} = this.context;
    return (
      <div>
        <Breadcrumbs>
          <Crumb active={true}>
            {project.name}
          </Crumb>
        </Breadcrumbs>
        <ScrollView>
          <ProjectTestListBody {...this.props} />
        </ScrollView>
      </div>
    );
  }
}

class ProjectTestListBody extends AsyncPage {
  getEndpoints() {
    let {orgName, projectName} = this.props.params;
    return [['testList', `/projects/${orgName}/${projectName}/tests`]];
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
