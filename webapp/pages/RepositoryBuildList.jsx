import React, {Component} from 'react';
import {connect} from 'react-redux';
import PropTypes from 'prop-types';

import {loadBuildsForRepository} from '../actions/builds';
import {subscribe} from '../decorators/stream';

import AsyncPage from '../components/AsyncPage';
import AsyncComponent from '../components/AsyncComponent';
import BuildList from '../components/BuildList';
import Paginator from '../components/Paginator';

class RepositoryBuildList extends AsyncPage {
  static propTypes = {
    ...AsyncPage.propTypes,
    repo: PropTypes.object.isRequired
  };

  renderBody() {
    return <BuildListBody {...this.props} />;
  }
}

class BuildListBody extends AsyncComponent {
  static propTypes = {
    repo: PropTypes.object.isRequired,
    buildList: PropTypes.array,
    links: PropTypes.object
  };

  fetchData() {
    return new Promise((resolve, reject) => {
      let {repo} = this.props;
      this.props.loadBuildsForRepository(repo.full_name, this.props.location.query);
      return resolve();
    });
  }

  renderBody() {
    return (
      <div>
        <BuildList
          params={this.props.params}
          buildList={this.props.buildList}
          repo={this.props.repo}
        />
        <Paginator links={this.props.links} {...this.props} />
      </div>
    );
  }
}

// We force the repo param into props so that we can read it as part of connect
// in order to filter down the data we're propagating to the child
// XXX(dcramer): this is super tricky/sketch atm
const DecoratedRepositoryBuildList = connect(
  ({builds, repo}) => ({
    buildList: builds.items.filter(
      build => !build.repository || build.repository.full_name === repo.full_name
    ),
    links: builds.links,
    loading: !builds.loaded
  }),
  {loadBuildsForRepository}
)(subscribe(({repo}) => [`repos:${repo.full_name}:builds`])(RepositoryBuildList));

export default class RepositoryBuildListWithRepoProp extends Component {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  render() {
    return <DecoratedRepositoryBuildList {...this.props} repo={this.context.repo} />;
  }
}
