import React from 'react';
import {connect} from 'react-redux';
import PropTypes from 'prop-types';

import {loadBuildsForRepository} from '../actions/builds';

import AsyncPage from '../components/AsyncPage';
import AsyncComponent from '../components/AsyncComponent';
import BuildList from '../components/BuildList';
import RepositoryContent from '../components/RepositoryContent';
import RepositoryHeader from '../components/RepositoryHeader';
import TabbedNav from '../components/TabbedNav';
import TabbedNavItem from '../components/TabbedNavItem';

class RepositoryBuildList extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  getTitle() {
    return this.context.repo.name;
  }

  renderBody() {
    let props = this.props;
    let repo = this.context.repo;
    let basePath = `/${repo.full_name}`;
    return (
      <div>
        <RepositoryHeader />
        <RepositoryContent {...this.props}>
          <TabbedNav>
            <TabbedNavItem
              to={{pathname: basePath, query: {}}}
              activeClassName=""
              className={
                props.location.pathname === basePath && !(props.location.query || {}).show
                  ? 'active'
                  : ''
              }>
              My Builds
            </TabbedNavItem>
            <TabbedNavItem
              to={{pathname: basePath, query: {show: 'all'}}}
              activeClassName="active">
              All Builds
            </TabbedNavItem>
          </TabbedNav>
          <BuildListBody {...this.props} />
        </RepositoryContent>
      </div>
    );
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
