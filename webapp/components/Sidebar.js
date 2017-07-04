import React, {Component} from 'react';
import styled from 'styled-components'

import Logo from '../assets/Logo';
import NavHeader from './NavHeader';
import SidebarRepoItem from './SidebarRepoItem';

const REPOSITORIES = [
  {
    id: 1,
    name: "getsentry/sentry",
    status: "pass",
    slug: "/"
  },
  {
    id: 2,
    name: "getsentry/getsentry",
    status: "fail",
    slug: "/something-else/"
  },
  {
    id: 3,
    name: "getsentry/freight",
    status: "pass",
    slug: "/something-else/"
  },
  {
    id: 4,
    name: "getsentry/sentry.io",
    status: "pass",
    slug: "/something-else/"
  },
  {
    id: 5,
    name: "getsentry/blog",
    status: "fail",
    slug: "/something-else/"
  },
];

export default class Sidebar extends Component {
  render() {
    return (
      <SidebarWrapper>
        <Logo size="30"/>
        <Hr />
        <SidebarNavHeader label="Repositories" />
        {REPOSITORIES.map((repo) =>
          <SidebarRepoItem key={repo.id}
            name={repo.name}
            status={repo.status}
            slug={repo.slug}
          />
        )}
      </SidebarWrapper>
    );
  }
}

const SidebarWrapper = styled.div`
  background: #39364E;
  color: #fff;
  padding: 18px 20px;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 220px;
`;

const Hr = styled.hr`
  background: none;
  border: 0;
  border-top: 1px solid #58617B;
  width: 30px;
  margin: 16px 0;
`;

const SidebarNavHeader = styled(NavHeader)`
  color: #8783A3;
  margin-bottom: 10px;
`;
