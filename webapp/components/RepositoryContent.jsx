import React from 'react';

import Section from '../components/Section';
import ScrollView from '../components/ScrollView';
import TabbedNav from '../components/TabbedNav';
import TabbedNavItem from '../components/TabbedNavItem';

export default props => {
  let {ownerName, repoName} = props.params;
  let basePath = `/${ownerName}/${repoName}`;
  return (
    <ScrollView>
      <TabbedNav>
        <TabbedNavItem
          to={basePath}
          query={{}}
          activeClassName=""
          className={
            props.location.pathname === basePath && !(props.location.query || {}).show
              ? 'active'
              : ''
          }>
          My builds
        </TabbedNavItem>
        <TabbedNavItem
          to={basePath}
          query={{show: 'all'}}
          activeClassName=""
          className={
            props.location.pathname === basePath &&
            (props.location.query || {}).show === 'all'
              ? 'active'
              : ''
          }>
          All builds
        </TabbedNavItem>
        <TabbedNavItem
          to={`${basePath}/tests`}
          activeClassName=""
          className={props.location.pathname === `${basePath}/tests` ? 'active' : ''}>
          Tests
        </TabbedNavItem>
      </TabbedNav>
      <Section>
        {props.children}
      </Section>
    </ScrollView>
  );
};
