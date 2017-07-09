import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';

import AsyncComponent from './AsyncComponent';
import BuildListItem from './BuildListItem';
import TabbedNavItem from './TabbedNavItem';

export default class BuildList extends AsyncComponent {
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
          {this.state.buildList.map(build => {
            return (
              <BuildListItem key={build.id} build={build} params={this.props.params} />
            );
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
