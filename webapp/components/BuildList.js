import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { Flex, Box } from 'grid-styled';

import AsyncComponent from './AsyncComponent';
import BuildListItem from './BuildListItem';
import Panel from './Panel';
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
          <Panel>
            <BuildListHeader>
              <Flex>
                <Box flex='1' width={6/12} pr={15}>
                  Build
                </Box>
                <Box width={2/12}>
                  Duration
                </Box>
                <Box width={2/12}>
                  Coverage
                </Box>
                <Box width={2/12}>
                  When
                </Box>
              </Flex>
            </BuildListHeader>
            <div>
              {this.state.buildList.map(build => {
                return (
                  <BuildListItem key={build.id} build={build} params={this.props.params} />
                );
              })}
            </div>
          </Panel>
        </ScrollView>
      </BuildIndex>
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

const BuildListHeader = styled.div`
  padding: 10px 15px;
  border-bottom: 1px solid #dbdae3;
  font-size: 13px;
  color: #767488;
  font-weight: 500;
  text-transform: uppercase;
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
