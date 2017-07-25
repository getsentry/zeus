import React from 'react';
import {connect} from 'react-redux';
import PropTypes from 'prop-types';

import {loadBuildsForRepository} from '../actions/builds';

import AsyncPage from '../components/AsyncPage';
import AsyncComponent from '../components/AsyncComponent';
import {Breadcrumbs, Crumb} from '../components/Breadcrumbs';
import BuildList from '../components/BuildList';
import Section from '../components/Section';
import ScrollView from '../components/ScrollView';
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
        <ScrollView>
          <TabbedNav>
            <TabbedNavItem to="/" activeNavClass="active">
              My builds
            </TabbedNavItem>
            <TabbedNavItem>All builds</TabbedNavItem>
          </TabbedNav>
          <Section>
            <BuildListBody {...this.props} />
          </Section>
        </ScrollView>
      </div>
    );
  }
}

class BuildListBody extends AsyncComponent {
  static propTypes = {
    buildList: PropTypes.array
  };

  fetchData() {
    let {ownerName, repoName} = this.props.params;
    this.props.loadBuildsForRepository(ownerName, repoName);
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
