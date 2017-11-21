import React from 'react';
import {Link} from 'react-router';
import {Flex} from 'grid-styled';
import styled from 'styled-components';
import {connect} from 'react-redux';
import PropTypes from 'prop-types';

import InProgressIcon from 'react-icons/lib/md/av-timer';
import CoverageIcon from 'react-icons/lib/md/blur-linear';

import {loadBuildsForUser} from '../actions/builds';
import {subscribe} from '../decorators/stream';

import AsyncPage from '../components/AsyncPage';
import AsyncComponent from '../components/AsyncComponent';
import BuildList from '../components/BuildList';
import {ButtonLink} from '../components/Button';
import Layout from '../components/Layout';
import ObjectCoverage from '../components/ObjectCoverage';
import ObjectDuration from '../components/ObjectDuration';
import Section from '../components/Section';
import SectionHeading from '../components/SectionHeading';

const RepoItem = styled.div`
  width: 33%;
  padding: 5px;
  flex-grow: 1;

  a {
    display: block;
    text-align: center;
    padding: 5px;
    border: 2px solid #111;
    color: #111;
    border-radius: 3px;
    overflow: hidden;

    svg {
      align-items: center;
      display: inline-block;
      margin-right: 5px;
      vertical-align: text-bottom !important;
    }

    &:hover {
      border-color: #7b6be6;
      background-color: #7b6be6;
      color: #fff;

      div {
        color: #fff;
      }
    }
  }
`;

const RepoName = styled.div`
  font-weight: 400;
  margin-bottom: 5px;
  white-space: nowrap;
`;

const RepoStats = styled.div`
  font-size: 0.8em;
  color: #666;
`;

const Stat = styled.span`
  &:last-child:after {
    display: none;
  }

  &:after {
    content: ' ';
    display: inline-block;
    margin: 0 5px;
  }
`;

class RepoListSection extends AsyncComponent {
  static propTypes = {
    repoList: PropTypes.array
  };

  renderBody() {
    return (
      <Flex>
        {this.props.repoList.map(repo => {
          return (
            <RepoItem key={repo.id} width="33%" p={5}>
              <Link to={repo.full_name}>
                <RepoName>{`${repo.owner_name} / ${repo.name}`}</RepoName>
                {repo.latest_build
                  ? <RepoStats>
                      <Stat>
                        <InProgressIcon size={14} />
                        <ObjectDuration data={repo.latest_build} />
                      </Stat>
                      {!!(
                        repo.latest_build.stats.coverage.lines_covered +
                        repo.latest_build.stats.coverage.lines_uncovered
                      ) &&
                        <Stat>
                          <CoverageIcon size={14} />
                          <ObjectCoverage data={repo.latest_build} diff={false} />
                        </Stat>}
                    </RepoStats>
                  : <RepoStats>(no data yet)</RepoStats>}
              </Link>
            </RepoItem>
          );
        })}
      </Flex>
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
