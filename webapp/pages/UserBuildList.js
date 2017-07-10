import React from 'react';
import styled from 'styled-components';

import AsyncComponent from '../components/AsyncComponent';
import BuildList from '../components/BuildList';
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
          <BuildBreadcrumbs>
            <UserName>
              {this.getTitle()}
            </UserName>
          </BuildBreadcrumbs>
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

const BuildBreadcrumbs = styled.div`
  background: #fff;
  padding: 20px;
  box-shadow: inset 0 -1px 0 #dbdae3;
`;

const UserName = styled.div`font-size: 22px;`;

const ScrollView = styled.div`
  position: absolute;
  top: 67px; /* TODO(ckj): calculate this dynamically */
  left: 0;
  right: 0;
  bottom: 0;
  overflow: auto;
  padding: 5px 20px 20px;
`;
