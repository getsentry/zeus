import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {Flex, Box} from 'grid-styled';

import api from '../api';
import AsyncPage from '../components/AsyncPage';
import Panel from '../components/Panel';
import ResultGridRow from '../components/ResultGridRow';
import Section from '../components/Section';
import SidebarLayout from '../components/SidebarLayout';

class GitHubRepoItem extends Component {
  static propTypes = {
    repo: PropTypes.object.isRequired,
    onDisableRepo: PropTypes.func.isRequired,
    onEnableRepo: PropTypes.func.isRequired
  };

  constructor(props, context) {
    super(props, context);
    this.state = {
      loading: false
    };
  }

  render() {
    let {repo} = this.props;
    return (
      <ResultGridRow>
        <Flex>
          <Box flex="1" width={11 / 12} pr={15}>
            {repo.name}
          </Box>
          <Box width={1 / 12} style={{textAlign: 'center'}}>
            {repo.loading
              ? '...'
              : repo.active
                ? <a onClick={this.props.onDisableRepo}>Disable</a>
                : <a onClick={this.props.onEnableRepo}>Enable</a>}
          </Box>
        </Flex>
      </ResultGridRow>
    );
  }
}

export default class GitHubRepositoryList extends AsyncPage {
  getTitle() {
    return 'GitHub Repositories';
  }

  getEndpoints() {
    return [['ghRepoList', '/github/repos']];
  }

  onDisableRepo(repoName) {
    throw new Error('Not implemented');
  }

  onEnableRepo(repoName) {
    let {ghRepoList} = this.state;
    let repo = ghRepoList.find(r => r.name === repoName);
    if (repo.loading || repo.active) return;
    repo.loading = true;

    // push the loading update
    this.setState(
      {
        ghRepoList: [...ghRepoList]
      },
      () => {
        api
          .post('/github/repos', {
            data: {
              name: repoName
            }
          })
          .then(_ => {
            let newRepoList = [...this.state.ghRepoList];
            let newRepo = newRepoList.find(r => r.name === repo.name);
            // update the item in place
            newRepo.active = true;
            newRepo.loading = false;
            this.setState({
              ghRepoList: newRepoList
            });
          });
      }
    );
  }

  render() {
    return (
      <SidebarLayout title={this.getTitle()}>
        <Section>
          <Panel>
            {this.renderContent()}
          </Panel>
        </Section>
      </SidebarLayout>
    );
  }

  renderBody() {
    return (
      <div>
        {this.state.ghRepoList.map(ghRepo => {
          return (
            <GitHubRepoItem
              key={ghRepo.name}
              repo={ghRepo}
              onEnableRepo={() => this.onEnableRepo(ghRepo.name)}
              onDisableRepo={() => this.onDisableRepo(ghRepo.name)}
            />
          );
        })}
      </div>
    );
  }
}
