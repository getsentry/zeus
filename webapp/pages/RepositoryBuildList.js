import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';

import AsyncPage from '../components/AsyncPage';
import {Breadcrumbs, Crumb} from '../components/Breadcrumbs';
import BuildList from '../components/BuildList';
import Section from '../components/Section';
import ScrollView from '../components/ScrollView';
import TabbedNavItem from '../components/TabbedNavItem';

export default class RepositoryBuildList extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  getTitle() {
    return this.context.repo.name;
  }

  renderBody() {
    let {repo} = this.context;
    return (
      <div>
        <Breadcrumbs>
          <Crumb active={true}>
            {repo.name}
          </Crumb>
        </Breadcrumbs>
        <ScrollView>
          <TabbedNav>
            <TabbedNavItem to="/" activeNavClass="active">
              My builds
            </TabbedNavItem>
            <TabbedNavItem>All builds</TabbedNavItem>
          </TabbedNav>
          <Section>
            <RepositoryBuildListBody {...this.props} />
          </Section>
        </ScrollView>
      </div>
    );
  }
}

class RepositoryBuildListBody extends AsyncPage {
  getEndpoints() {
    let {ownerName, repoName} = this.props.params;
    return [['buildList', `/repos/${ownerName}/${repoName}/builds`]];
  }

  renderBody() {
    return <BuildList params={this.props.params} buildList={this.state.buildList} />;
  }
}

const TabbedNav = styled.div`
  overflow: hidden;
  margin: 0 20px 20px;
  box-shadow: inset 0 -1px 0 #dbdae3;
`;
