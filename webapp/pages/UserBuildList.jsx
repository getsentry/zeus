import React from 'react';
import {connect} from 'react-redux';
import PropTypes from 'prop-types';

import {loadBuildsForUser} from '../actions/builds';
import {subscribe} from '../decorators/stream';

import AsyncPage from '../components/AsyncPage';
import AsyncComponent from '../components/AsyncComponent';
import BuildList from '../components/BuildList';
import Layout from '../components/Layout';
import Paginator from '../components/Paginator';
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
      <div>
        <h2>Your Builds</h2>
        <BuildList
          params={this.props.params}
          buildList={this.props.buildList}
          includeAuthor={false}
          includeRepo={true}
        />
        <Paginator links={this.props.links} {...this.props} />
      </div>
    );
  }
}

export default connect(
  ({auth, builds}) => {
    let emailSet = new Set((auth.emails || []).map(e => e.email));
    return {
      buildList: builds.items.filter(
        build => !!build.repository && emailSet.has(build.source.author.email)
      ),
      links: builds.links,
      loading: !builds.loaded
    };
  },
  {loadBuildsForUser}
)(subscribe(() => ['builds'])(UserBuildList));
