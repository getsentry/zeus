import React, {Component} from 'react';
import styled from 'styled-components'

import Logo from '../assets/Logo';
import NavHeading from './NavHeading';
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
        <SidebarNavHeading label="Repositories" />
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
  background-image: linear-gradient(rgba(123,107,230,0.10) 25%, rgba(118,211,146,0.10) 100%);
  box-shadow: inset -5px 0 10px rgba(0,0,0, .1);
`;

const SidebarNavHeading = styled(NavHeading)`
  color: #8783A3;
  margin-top: 20px;
  margin-bottom: 10px;
  font-weight: 400;
`;
