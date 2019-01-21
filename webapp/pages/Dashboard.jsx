import React from 'react';
import {Flex, Box} from 'grid-styled';
import {Link} from 'react-router';
import styled from 'styled-components';
import {connect} from 'react-redux';
import PropTypes from 'prop-types';

import ViewAllIcon from 'react-icons/lib/md/input';

import {fetchBuilds} from '../actions/builds';
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
          <SectionHeading>Your Repositories</SectionHeading>
          <p>
            {"Looks like you haven't yet setup any repositories. "}
            <Link to="/settings/github/repos">Add a repository</Link> to get started.
          </p>
        </Section>
      );
    }

    return (
      <Section>
        <SectionHeading>
          Your Repositories
          <Link to="/settings/github/repos" style={{marginLeft: 10}}>
            <ViewAllIcon size={18} style={{verticalAlign: 'text-bottom'}} />
          </Link>
        </SectionHeading>
        <ResultGrid>
          <Header>
            <Column>Repository</Column>
            <Column textAlign="center" width={90} hide="md">
              Coverage
            </Column>
            <Column textAlign="center" width={90} hide="sm">
              Duration
            </Column>
          </Header>
          <Collapsable collapsable maxVisible={10}>
            {this.props.repoList.map(repo => {
              let {latest_build} = repo;
              return (
                <RepoLink to={repo.full_name} key={repo.id}>
                  <Row>
                    <Column>
                      <Name>{`${repo.owner_name} / ${repo.name}`}</Name>
                    </Column>
                    <Column textAlign="center" width={90} hide="md">
                      {!!latest_build &&
                        !!(
                          latest_build.stats.coverage.lines_covered +
                          latest_build.stats.coverage.lines_uncovered
                        ) && <ObjectCoverage data={latest_build} diff={false} />}
                    </Column>
                    <Column textAlign="center" width={90} hide="sm">
                      {!!latest_build && <ObjectDuration data={latest_build} />}
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

const WrappedRepoList = connect(
  function(state) {
    return {repoList: state.repos.items, loading: !state.repos.loaded};
  },
  {}
)(RepoListSection);

class BuildListSection extends AsyncComponent {
  static propTypes = {
    buildList: PropTypes.array
  };

  loadData() {
    return new Promise(resolve => {
      this.props.fetchBuilds({user: 'me', per_page: 10});
      return resolve();
    });
  }

  renderContent() {
    return (
      <Section>
        <SectionHeading>
          Your Builds
          <Link to="/builds" style={{marginLeft: 10}}>
            <ViewAllIcon size={18} style={{verticalAlign: 'text-bottom'}} />
          </Link>
        </SectionHeading>
        {super.renderContent()}
      </Section>
    );
  }

  renderBody() {
    if (!this.props.buildList.length) {
      return <p>No builds yet</p>;
    }
    return (
      <BuildList
        columns={['date']}
        params={this.props.params}
        buildList={this.props.buildList}
        includeAuthor={false}
        includeRepo={true}
      />
    );
  }
}

const WrappedBuildList = connect(
  ({auth, builds}) => {
    let emailSet = new Set((auth.emails || []).map(e => e.email));
    return {
      buildList: builds.items
        .filter(build => !!build.repository && emailSet.has(build.source.author.email))
        .slice(0, 10),
      loading: !builds.loaded
    };
  },
  {fetchBuilds}
)(subscribe(() => ['builds'])(BuildListSection));

export default class Dashboard extends AsyncPage {
  getTitle() {
    return 'Zeus Dashboard';
  }

  renderBody() {
    return (
      <Layout withHeader>
        <Flex flex="1">
          <Box width={7 / 12} mr={30}>
            <WrappedBuildList {...this.props} />
          </Box>
          <Box width={5 / 12}>
            <WrappedRepoList {...this.props} />
          </Box>
        </Flex>
      </Layout>
    );
  }
}

const Name = styled.div`
  font-size: 15px;
  line-height: 1.2;
  font-weight: 500;
  text-overflow: ellipsis;
  white-space: nowrap;
  overflow: hidden;
`;
