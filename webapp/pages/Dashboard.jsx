import React from 'react';
import {Link} from 'react-router';
import styled from 'styled-components';
import {connect} from 'react-redux';
import PropTypes from 'prop-types';

import ViewAllIcon from 'react-icons/lib/md/input';

import {loadBuildsForUser} from '../actions/builds';
import {subscribe} from '../decorators/stream';

import AsyncPage from '../components/AsyncPage';
import AsyncComponent from '../components/AsyncComponent';
import BuildList from '../components/BuildList';
import Collapsable from '../components/Collapsable';
import Layout from '../components/Layout';
import ObjectCoverage from '../components/ObjectCoverage';
import ObjectDuration from '../components/ObjectDuration';
import {Column, Header, ResultGrid, Row} from '../components/ResultGrid';
import Section from '../components/Section';
import SectionHeading from '../components/SectionHeading';

const RepoLink = styled(Link)`
  display: block;
  cursor: pointer;

  &:hover {
    background-color: #f0eff5;
  }
`;

class RepoListSection extends AsyncComponent {
  static propTypes = {
    repoList: PropTypes.array
  };

  renderBody() {
    if (!this.props.repoList.length) {
      return (
        <Section>
          <p>
            {"Looks like you haven't yet setup and repositories. "}
            <Link to="/settings/github/repos">Add a repository</Link> to get started.
          </p>
        </Section>
      );
    }

    return (
      <Section>
        <ResultGrid>
          <Header>
            <Column>Repository</Column>
            <Column textAlign="center" width={90} hide="sm">
              Coverage
            </Column>
            <Column textAlign="center" width={90} hide="sm">
              Duration
            </Column>
          </Header>
          <Collapsable collapsable maxVisible={5}>
            {this.props.repoList.map(repo => {
              return (
                <RepoLink to={repo.full_name} key={repo.id}>
                  <Row>
                    <Column>
                      <strong>{`${repo.owner_name} / ${repo.name}`}</strong>
                    </Column>
                    <Column textAlign="center" width={90} hide="sm">
                      {!!repo.latest_build &&
                        !!(
                          repo.latest_build.stats.coverage.lines_covered +
                          repo.latest_build.stats.coverage.lines_uncovered
                        ) &&
                        <ObjectCoverage data={repo.latest_build} diff={false} />}
                    </Column>
                    <Column textAlign="center" width={90} hide="sm">
                      {!!repo.latest_build && <ObjectDuration data={repo.latest_build} />}
                    </Column>
                  </Row>
                </RepoLink>
              );
            })}
          </Collapsable>
        </ResultGrid>
      </Section>
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
      this.props.loadBuildsForUser('me', {per_page: 10});
      return resolve();
    });
  }

  renderBody() {
    if (!this.props.buildList.length) {
      return null;
    }
    return (
      <Section>
        <SectionHeading>
          Your Builds
          <Link to="/builds" style={{marginLeft: 10}}>
            <ViewAllIcon size={18} style={{verticalAlign: 'text-bottom'}} />
          </Link>
        </SectionHeading>
        <BuildList
          params={this.props.params}
          buildList={this.props.buildList}
          includeAuthor={false}
          includeRepo={true}
        />
      </Section>
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
        <WrappedRepoList {...this.props} />
        <WrappedBuildList {...this.props} />
      </Layout>
    );
  }
}
