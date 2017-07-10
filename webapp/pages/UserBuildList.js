import React from 'react';
import styled from 'styled-components';

import AsyncComponent from '../components/AsyncComponent';
import {Breadcrumbs, Crumb} from '../components/Breadcrumbs';
import BuildList from '../components/BuildList';
import ScrollView from '../components/ScrollView';
import Sidebar from '../components/Sidebar';

export default class RepositoryBuildList extends AsyncComponent {
  getTitle() {
    let {userID} = this.props.params;
    return userID ? 'Builds' : 'My Builds';
  }

  renderBody() {
    return (
      <div>
        <Sidebar params={this.props.params} />
        <BuildIndex>
          <Breadcrumbs>
            <Crumb active={true}>
              {this.getTitle()}
            </Crumb>
          </Breadcrumbs>
          <ScrollView>
            <UserBuildListBody {...this.props} />
          </ScrollView>
        </BuildIndex>
      </div>
    );
  }
}

class UserBuildListBody extends AsyncComponent {
  getEndpoints() {
    let {userID} = this.props.params;
    return [['buildList', `/users/${userID || 'me'}/builds`]];
  }

  renderBody() {
    return <BuildList params={this.props.params} buildList={this.state.buildList} />;
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
