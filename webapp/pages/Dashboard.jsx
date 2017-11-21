import React from 'react';
import {Link} from 'react-router';
import {connect} from 'react-redux';
import PropTypes from 'prop-types';

import {loadBuildsForUser} from '../actions/builds';
import {subscribe} from '../decorators/stream';

import AsyncPage from '../components/AsyncPage';
import AsyncComponent from '../components/AsyncComponent';
import BuildList from '../components/BuildList';
import {ButtonLink} from '../components/Button';
import Layout from '../components/Layout';
import Section from '../components/Section';
import SectionHeading from '../components/SectionHeading';

class RepoListSection extends AsyncComponent {
  static propTypes = {
    repoList: PropTypes.array
  };

  renderBody() {
    return (
      <ul>
        {this.props.repoList.map(repo => {
          return (
            <li key={repo.id}>
              <Link to={repo.full_name}>{`${repo.owner_name} / ${repo.name}`}</Link>
            </li>
          );
        })}
      </ul>
    );
  }
}

const WrappedRepoList = connect(function(state) {
  return {repoList: state.repos.items, loading: !state.repos.loaded};
}, {})(RepoListSection);

class BuildListSection extends AsyncComponent {
  static propTypes = {
    buildList: PropTypes.array
  };

  fetchData() {
    return new Promise((resolve, reject) => {
      this.props.loadBuildsForUser('me', 10);
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

const WrappedBuildList = connect(
  function(state) {
    let emailSet = new Set((state.auth.emails || []).map(e => e.email));
    return {
      buildList: state.builds.items.filter(build =>
        emailSet.has(build.source.author.email)
      ),
      loading: !state.builds.loaded
    };
  },
  {loadBuildsForUser}
)(subscribe((props, {repo}) => ['builds'])(BuildListSection));

export default class Dashboard extends AsyncPage {
  getTitle() {
    return 'Zeus Dashboard';
  }

  renderBody() {
    return (
      <Layout>
        <Section>
          <SectionHeading>
            Repositories
            <ButtonLink
              to="/settings/github/repos"
              size="xs"
              style={{marginLeft: 10, verticalAlign: 'text-bottom'}}>
              &middot; &middot; &middot;
            </ButtonLink>
          </SectionHeading>
          <WrappedRepoList {...this.props} />
        </Section>
        <Section>
          <SectionHeading>
            Your Builds
            <ButtonLink
              to="/builds"
              size="xs"
              style={{marginLeft: 10, verticalAlign: 'text-bottom'}}>
              &middot; &middot; &middot;
            </ButtonLink>
          </SectionHeading>
          <WrappedBuildList {...this.props} />
        </Section>
      </Layout>
    );
  }
}
