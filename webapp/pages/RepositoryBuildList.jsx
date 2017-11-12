import React, {Component} from 'react';
import {connect} from 'react-redux';
import PropTypes from 'prop-types';

import {loadBuildsForRepository} from '../actions/builds';
import {subscribe} from '../decorators/stream';

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

// We force the repo param into props so that we can read it as part of connect
// in order to filter down the data we're propagating to the child
const DecoratedRepositoryBuildList = connect(
  ({builds}, {repo}) => ({
    buildList: builds.items.filter(
      build => build.repository.full_name === repo.full_name
    ),
    loading: !builds.loaded
  }),
  {loadBuildsForRepository}
)(subscribe((props, {repo}) => [`repos:${repo.full_name}:builds`])(RepositoryBuildList));

class RepositoryBuildListWithRepoProp extends Component {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  render() {
    return <DecoratedRepositoryBuildList {...this.props} repo={this.context.repo} />;
  }
}

export default RepositoryBuildListWithRepoProp;
