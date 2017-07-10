import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';

import AsyncComponent from '../components/AsyncComponent';
import BuildList from '../components/BuildList';
import Sidebar from '../components/Sidebar';
import TabbedNavItem from '../components/TabbedNavItem';

export default class RepositoryBuildList extends AsyncComponent {
  static contextTypes = {
    ...AsyncComponent.contextTypes,
    repo: PropTypes.object.isRequired
  };

  getEndpoints() {
    let {repoName} = this.props.params;
    return [['buildList', `/repos/${repoName}/builds`]];
  }

  renderBody() {
    let {repo} = this.context;
    return (
      <div>
        <Sidebar params={this.props.params} />
        <BuildIndex>
          <BuildBreadcrumbs>
            <RepositoryName>
              {repo.name}
            </RepositoryName>
          </BuildBreadcrumbs>
          <ScrollView>
            <TabbedNav>
              <TabbedNavItem to="/" activeNavClass="active">
                My builds
              </TabbedNavItem>
              <TabbedNavItem>All builds</TabbedNavItem>
            </TabbedNav>
            <BuildList params={this.props.params} buildList={this.state.buildList} />
          </ScrollView>
        </BuildIndex>
      </div>
    );
  }
}

const BuildIndex = styled.div`
  position: fixed;
  top: 0;
  left: 220px;
  bottom: 0;
  right: 0;
  background: #f8f9fb;
`;

const BuildBreadcrumbs = styled.div`
  background: #fff;
  padding: 20px;
  box-shadow: inset 0 -1px 0 #dbdae3;
`;

const RepositoryName = styled.div`font-size: 22px;`;

const TabbedNav = styled.div`
  overflow: hidden;
  margin-bottom: 20px;
  box-shadow: inset 0 -1px 0 #dbdae3;
`;

const ScrollView = styled.div`
  position: absolute;
  top: 67px; /* TODO(ckj): calculate this dynamically */
  left: 0;
  right: 0;
  bottom: 0;
  overflow: auto;
  padding: 5px 20px 20px;
`;
