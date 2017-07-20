import React, {Component} from 'react';
import {Link} from 'react-router';
import {connect} from 'react-redux';
import PropTypes from 'prop-types';
import {Flex, Box} from 'grid-styled';

import {addIndicator, removeIndicator} from '../actions/indicators';
import {addRepo, removeRepo, updateRepo} from '../actions/repos';
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
                ? <a onClick={this.props.onDisableRepo} style={{cursor: 'pointer'}}>
                    Disable
                  </a>
                : <a onClick={this.props.onEnableRepo} style={{cursor: 'pointer'}}>
                    Enable
                  </a>}
          </Box>
        </Flex>
      </ResultGridRow>
    );
  }
}

class GitHubRepositoryList extends AsyncPage {
  getTitle() {
    return 'GitHub Repositories';
  }

  getEndpoints() {
    return [
      ['ghOrgList', '/github/orgs'],
      [
        'ghRepoList',
        '/github/repos',
        {
          query: this.props.location.query
        }
      ]
    ];
  }

  onToggleRepo = (repoName, active = null) => {
    let {ghRepoList} = this.state;
    let ghRepo = ghRepoList.find(r => r.name === repoName);
    if (active === null) active = !ghRepo.active;
    if (ghRepo.loading || ghRepo.active === active) return;
    ghRepo.loading = true;

    // push the loading update
    let indicator = this.props.addIndicator('Saving changes..', 'loading');
    this.setState(
      {
        ghRepoList: [...ghRepoList]
      },
      () => {
        this.api
          .request('/github/repos', {
            method: active ? 'POST' : 'DELETE',
            data: {
              name: repoName
            }
          })
          .then(repo => {
            let newGhRepoList = [...this.state.ghRepoList];
            let newGhRepo = newGhRepoList.find(r => r.name === ghRepo.name);
            // update the item in place
            newGhRepo.active = active;
            newGhRepo.loading = false;
            if (active) {
              this.props.addRepo(repo);
            } else {
              this.props.removeRepo(repo);
            }
            this.props.removeIndicator(indicator);
            this.setState({
              ghRepoList: newGhRepoList
            });
          })
          .catch(error => {
            this.props.addIndicator('An error occurred.', 'error', 5000);
            this.props.removeIndicator(indicator);
            throw error;
          });
      }
    );
  };

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
      <Flex>
        <Box flex="1" width={2 / 12} pr={15}>
          <ul>
            <li key="_">
              <Link
                to={{
                  query: {},
                  pathname: this.props.location.pathname
                }}>
                mine
              </Link>
            </li>
            {this.state.ghOrgList.map(ghOrg => {
              return (
                <li key={ghOrg.name}>
                  <Link
                    to={{
                      query: {orgName: ghOrg.name},
                      pathname: this.props.location.pathname
                    }}>
                    {ghOrg.name}
                  </Link>
                </li>
              );
            })}
          </ul>
        </Box>
        <Box width={10 / 12}>
          {this.state.ghRepoList.map(ghRepo => {
            return (
              <GitHubRepoItem
                key={ghRepo.name}
                repo={ghRepo}
                onEnableRepo={() => this.onToggleRepo(ghRepo.name, true)}
                onDisableRepo={() => this.onToggleRepo(ghRepo.name, false)}
              />
            );
          })}
        </Box>
      </Flex>
    );
  }
}

export default connect(null, {
  addIndicator,
  removeIndicator,
  addRepo,
  removeRepo,
  updateRepo
})(GitHubRepositoryList);
