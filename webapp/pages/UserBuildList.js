import React from 'react';

import AsyncPage from '../components/AsyncPage';
import BuildList from '../components/BuildList';
import Section from '../components/Section';
import SidebarLayout from '../components/SidebarLayout';

export default class RepositoryBuildList extends AsyncPage {
  getTitle() {
    let {userID} = this.props.params;
    return userID ? 'Builds' : 'My Builds';
  }

  renderBody() {
    return (
      <SidebarLayout title={this.getTitle()}>
        <Section>
          <UserBuildListBody {...this.props} />
        </Section>
      </SidebarLayout>
    );
  }
}

class UserBuildListBody extends AsyncPage {
  getEndpoints() {
    let {userID} = this.props.params;
    return [['buildList', `/users/${userID || 'me'}/builds`]];
  }

  renderBody() {
    return <BuildList params={this.props.params} buildList={this.state.buildList} />;
  }
}
