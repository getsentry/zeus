import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import Content from '../components/Content';
import Sidebar from '../components/Sidebar';

export default class ProjectDetails extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    projectList: PropTypes.arrayOf(PropTypes.object).isRequired
  };

  static childContextTypes = {
    ...AsyncPage.childContextTypes,
    ...ProjectDetails.contextTypes,
    project: PropTypes.object.isRequired
  };

  getChildContext() {
    return {
      ...this.context,
      project: this.state.project
    };
  }

  getDefaultState(props, context) {
    let {orgName, projectName} = props.params;
    let {projectList} = context;
    let state = super.getDefaultState(props, context);
    state.project = projectList.find(
      r => r.organization.name === orgName && r.name === projectName
    );
    return state;
  }

  getTitle() {
    return this.state.project.name;
  }

  renderBody() {
    return (
      <div>
        <Sidebar params={this.props.params} />
        <Content>
          {this.props.children}
        </Content>
      </div>
    );
  }
}
