import React from 'react';
import {connect} from 'react-redux';
import PropTypes from 'prop-types';

import {loadBuildsForUser} from '../actions/builds';
import {subscribe} from '../decorators/stream';

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
    buildList: PropTypes.array,
    links: PropTypes.array
  };

  fetchData() {
    return new Promise((resolve, reject) => {
      this.props.loadBuildsForUser('me', {
        per_page: 25,
        page: this.props.location.query.page || 1
      });
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
    let emailSet = new Set((state.auth.emails || []).map(e => e.email));
    return {
      buildList: state.builds.items.filter(build =>
        emailSet.has(build.source.author.email)
      ),
      links: state.builds.links,
      loading: !state.builds.loaded
    };
  },
  {loadBuildsForUser}
)(subscribe((props, {repo}) => ['builds'])(UserBuildList));
