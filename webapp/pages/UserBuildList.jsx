import React from 'react';
import {connect} from 'react-redux';
import PropTypes from 'prop-types';

import {loadBuildsForUser} from '../actions/builds';

import AsyncPage from '../components/AsyncPage';
import AsyncComponent from '../components/AsyncComponent';
import BuildList from '../components/BuildList';
import Layout from '../components/Layout';
import Section from '../components/Section';

class UserBuildList extends AsyncPage {
  getTitle() {
    let {userID} = this.props.params;
    return userID ? 'Builds' : 'My Builds';
  }

  renderBody() {
    return (
      <Layout title={this.getTitle()}>
        <Section>
          <BuildListBody {...this.props} />
        </Section>
      </Layout>
    );
  }
}

class BuildListBody extends AsyncComponent {
  static propTypes = {
    buildList: PropTypes.array
  };

  fetchData() {
    return new Promise((resolve, reject) => {
      this.props.loadBuildsForUser();
      return resolve();
    });
  }

  renderBody() {
    return (
      <BuildList
        params={this.props.params}
        buildList={this.props.buildList}
        includeAuthor={false}
        includeRepo={true}
      />
    );
  }
}

export default connect(
  function(state) {
    return {
      buildList: state.builds.items,
      loading: !state.builds.loaded
    };
  },
  {loadBuildsForUser}
)(UserBuildList);
