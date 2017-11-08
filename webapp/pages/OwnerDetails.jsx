import React from 'react';
import {Link} from 'react-router';
import PropTypes from 'prop-types';

import {ResourceNotFound} from '../errors';
import AsyncPage from '../components/AsyncPage';
import {Breadcrumbs, CrumbLink} from '../components/Breadcrumbs';
import Content from '../components/Content';
import Header from '../components/Header';
import ResultGrid from '../components/ResultGrid';
import Section from '../components/Section';
import ScrollView from '../components/ScrollView';
import Sidebar from '../components/Sidebar';

export default class OwnerDetails extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repoList: PropTypes.arrayOf(PropTypes.object).isRequired
  };

  static childContextTypes = {
    ...AsyncPage.childContextTypes,
    ...OwnerDetails.contextTypes
  };

  getDefaultState(props, context) {
    let {ownerName, provider} = props.params;
    let {repoList} = context;
    let state = super.getDefaultState(props, context);
    state.repoList = repoList.filter(
      r => r.owner_name === ownerName && r.provider == provider
    );
    if (!state.repoList.length) {
      throw new ResourceNotFound('No repositories found or you do not have access');
    }
    return state;
  }

  getTitle() {
    let {ownerName} = this.props.params;
    return ownerName;
  }

  renderBody() {
    let {provider, ownerName} = this.props.params;
    return (
      <div>
        <Sidebar params={this.props.params} />
        <Content>
          <Header>
            <Breadcrumbs>
              <CrumbLink to={`/${provider}/${ownerName}`}>
                {ownerName}
              </CrumbLink>
            </Breadcrumbs>
          </Header>
          <ScrollView>
            <Section>
              <ResultGrid.ResultGrid>
                <ResultGrid.Header>
                  <ResultGrid.Column>Repository</ResultGrid.Column>
                </ResultGrid.Header>
                {this.state.repoList.map(repo => {
                  return (
                    <ResultGrid.Row key={repo.name}>
                      <ResultGrid.Column>
                        <Link to={`/${repo.full_name}`}>
                          {repo.name}
                        </Link>
                        <br />
                        {!!repo.url &&
                          <small>
                            {repo.url}
                          </small>}
                      </ResultGrid.Column>
                    </ResultGrid.Row>
                  );
                })}
              </ResultGrid.ResultGrid>
            </Section>
          </ScrollView>
        </Content>
      </div>
    );
  }
}
