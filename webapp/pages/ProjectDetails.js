import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';

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
    let {params} = this.props;
    return `${params.orgName}/${params.projectName}`;
  }

  renderBody() {
    return this.props.children;
  }
}
