import React from 'react';

import AsyncPage from '../components/AsyncPage';
import {Breadcrumbs, Crumb} from '../components/Breadcrumbs';
import BuildList from '../components/BuildList';
import Content from '../components/Content';
import Section from '../components/Section';
import ScrollView from '../components/ScrollView';
import Sidebar from '../components/Sidebar';

export default class RepositoryBuildList extends AsyncPage {
  getTitle() {
    let {userID} = this.props.params;
    return userID ? 'Builds' : 'My Builds';
  }

  renderBody() {
    return (
      <div>
        <Sidebar params={this.props.params} />
        <Content>
          <Breadcrumbs>
            <Crumb active={true}>
              {this.getTitle()}
            </Crumb>
          </Breadcrumbs>
          <ScrollView>
            <Section>
              <UserBuildListBody {...this.props} />
            </Section>
          </ScrollView>
        </Content>
      </div>
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
