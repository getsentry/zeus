import React from 'react';
import {connect} from 'react-redux';
import PropTypes from 'prop-types';

import {loadBuildsForRepository} from '../actions/builds';

import AsyncPage from '../components/AsyncPage';
import AsyncComponent from '../components/AsyncComponent';
import BuildList from '../components/BuildList';

class RepositoryBuildList extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  getTitle() {
    return this.context.repo.name;
  }

  renderBody() {
    return <BuildListBody {...this.props} />;
  }
}

class BuildListBody extends AsyncComponent {
  static propTypes = {
    buildList: PropTypes.array
  };

  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  fetchData(refresh) {
    return new Promise((resolve, reject) => {
      let {repo} = this.context;
      this.props.loadBuildsForRepository(
        repo.full_name,
        this.props.location.query,
        !refresh
      );
      return resolve();
    });
  }

  renderBody() {
    return <BuildList params={this.props.params} buildList={this.props.buildList} />;
  }
}

export default connect(
  function(state) {
    return {
      buildList: state.builds.items,
      loading: !state.builds.loaded
    };
  },
  {loadBuildsForRepository}
)(RepositoryBuildList);
