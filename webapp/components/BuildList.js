import React, {Component} from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';

import BuildListItem from './BuildListItem';
import TabbedNavItem from './TabbedNavItem';

const BUILDS = [
  {
    id: 1,
    message: 'make this work again',
    status: 'pass',
    duration: '6 mins',
    timestamp: '1m ago',
    author: 'dcramer',
    branch: 'master',
    commit: '11d655b',
    slug: '/somewhere-else/',
    testCount: 47,
    lineCoverageDiff: 1
  },
  {
    id: 2,
    message: 'various improvements',
    status: 'pass',
    duration: '12 mins',
    timestamp: '2h ago',
    author: 'dcramer',
    branch: 'ui/fix-that-thing',
    commit: '11d655b',
    slug: '/',
    testCount: 47,
    lineCoverageDiff: 1
  },
  {
    id: 3,
    message: 'fix stuff',
    status: 'fail',
    duration: '3 mins',
    timestamp: '2h ago',
    author: 'dcramer',
    branch: 'bug/wtf-did-we-do',
    commit: '11d655b',
    slug: '/somewhere-else',
    testCount: 47,
    lineCoverageDiff: 0.9
  },
  {
    id: 4,
    message: 'new sidebar lol',
    status: 'pass',
    duration: '2 mins',
    timestamp: '3h ago',
    author: 'dcramer',
    branch: 'master',
    commit: '11d655b',
    slug: '/somewhere-else',
    testCount: 47,
    lineCoverageDiff: 0.95
  },
  {
    id: 5,
    message: 'resolve merge conflicts',
    status: 'pass',
    duration: '6 mins',
    timestamp: '4h ago',
    author: 'dcramer',
    branch: 'master',
    commit: '11d655b',
    slug: '/somewhere-else',
    testCount: 47,
    lineCoverageDiff: 1
  },
  {
    id: 6,
    message: 'do this one other thing',
    status: 'fail',
    duration: '2 mins',
    timestamp: '5h ago',
    author: 'dcramer',
    branch: 'master',
    commit: '11d655b',
    slug: '/somewhere-else',
    testCount: 47,
    lineCoverageDiff: 1
  },
  {
    id: 7,
    message: 'various improvements',
    status: 'fail',
    duration: '6 mins',
    timestamp: '7h ago',
    author: 'dcramer',
    branch: 'master',
    commit: '11d655b',
    slug: '/somewhere-else',
    testCount: 47,
    lineCoverageDiff: 0.96
  },
  {
    id: 8,
    message: 'random stuff',
    status: 'pass',
    duration: '12 mins',
    timestamp: '8h ago',
    author: 'dcramer',
    branch: 'master',
    commit: '11d655b',
    slug: '/somewhere-else',
    testCount: 47,
    lineCoverageDiff: 0.96
  },
  {
    id: 9,
    message: 'merge stuff',
    status: 'pass',
    duration: '8 mins',
    timestamp: '9h ago',
    author: 'dcramer',
    branch: 'master',
    commit: '11d655b',
    slug: '/somewhere-else',
    testCount: 47,
    lineCoverageDiff: 0.94
  },
  {
    id: 10,
    message: 'um i hope this works',
    status: 'fail',
    duration: '13 mins',
    timestamp: '12h ago',
    author: 'dcramer',
    branch: 'master',
    commit: '11d655b',
    slug: '/somewhere-else',
    testCount: 47,
    lineCoverageDiff: 0.94
  },
  {
    id: 11,
    message: 'TODO: fix this',
    status: 'fail',
    duration: '13 mins',
    timestamp: '1d ago',
    author: 'dcramer',
    branch: 'master',
    commit: '11d655b',
    slug: '/somewhere-else',
    testCount: 47,
    lineCoverageDiff: 0.94
  },
  {
    id: 12,
    message: 'maybe one day this will do',
    status: 'pass',
    duration: '13 mins',
    timestamp: '1d ago',
    author: 'dcramer',
    branch: 'master',
    commit: '11d655b',
    slug: '/somewhere-else',
    testCount: 47,
    lineCoverageDiff: 0.94
  },
  {
    id: 13,
    message: 'gotta make sure it scrolls',
    status: 'pass',
    duration: '14 mins',
    timestamp: '2d ago',
    author: 'dcramer',
    branch: 'master',
    commit: '11d655b',
    slug: '/somewhere-else',
    testCount: 47,
    lineCoverageDiff: 0.95
  },
  {
    id: 14,
    message: 'one last one for good luck',
    status: 'fail',
    duration: '14 mins',
    timestamp: '3d ago',
    author: 'dcramer',
    branch: 'master',
    commit: '11d655b',
    slug: '/somewhere-else',
    testCount: 47,
    lineCoverageDiff: 0.95
  }
];

export default class BuildList extends Component {
  static contextTypes = {
    repo: PropTypes.object.isRequired
  };

  render() {
    let {repo} = this.context;
    return (
      <BuildListWrapper>
        <BuildListHeader>
          <RepositoryName>
            {repo.name}
          </RepositoryName>
          <TabbedNav>
            <TabbedNavItem to="/" activeNavClass="active">
              My builds
            </TabbedNavItem>
            <TabbedNavItem>All builds</TabbedNavItem>
          </TabbedNav>
        </BuildListHeader>
        <ScrollView>
          {BUILDS.map(build => {
            return <BuildListItem key={build.id} build={build} />;
          })}
        </ScrollView>
      </BuildListWrapper>
    );
  }
}

const BuildListWrapper = styled.div`
  position: fixed;
  top: 0;
  left: 220px;
  bottom: 0;
  right: 0;
  background: #f8f9fb;
  box-shadow: inset -1px 0 0 #dbdae3;
`;

const BuildListHeader = styled.div`
  background: #fff;
  padding: 15px 20px 0;
  box-shadow: inset 0 -1px 0 #dbdae3;
  margin-right: 1px;
`;

const RepositoryName = styled.div`font-size: 22px;`;

const TabbedNav = styled.div`overflow: hidden;`;

const ScrollView = styled.div`
  position: absolute;
  top: 93px; /* TODO(ckj): calculate this dynamically */
  left: 0;
  right: 0;
  bottom: 0;
  overflow: auto;
`;
