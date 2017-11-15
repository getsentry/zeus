import sortBy from 'lodash/sortBy';
import React, {Component} from 'react';
import {Link} from 'react-router';
import {connect} from 'react-redux';
import PropTypes from 'prop-types';
import {Flex, Box} from 'grid-styled';

import {addIndicator, removeIndicator} from '../actions/indicators';
import {addRepo, removeRepo, updateRepo} from '../actions/repos';
import AsyncPage from '../components/AsyncPage';
import Button from '../components/Button';
import {ResultGrid, Row, Column} from '../components/ResultGrid';

class GitHubRepoItem extends Component {
  static propTypes = {
    repo: PropTypes.object.isRequired,
    onDisableRepo: PropTypes.func,
    onEnableRepo: PropTypes.func
  };

  constructor(props, context) {
    super(props, context);
    this.state = {
      loading: false
    };
  }

  renderButton() {
    let {repo} = this.props;

    if (repo.active) {
      return (
        <Button onClick={this.props.onDisableRepo} size="small" type="danger">
          Disable
        </Button>
      );
    }

    if (repo.admin) {
      return (
        <Button onClick={this.props.onEnableRepo} size="small">
          Enable
        </Button>
      );
    }

    return (
      <Button
        disabled
        size="small"
        title="You need administrator privileges to activate this repository">
        Enable
      </Button>
    );
  }

  render() {
    let {repo} = this.props;
    return (
      <Row>
        <Column>{repo.name}</Column>
        <Column textAlign="right" width={80}>
          {repo.loading ? '...' : this.renderButton()}
        </Column>
      </Row>
    );
  }
}

class GitHubRepositoryList extends AsyncPage {
  static propTypes = {
    ...AsyncPage.propTypes,
    identities: PropTypes.object.isRequired
  };

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
          query: {
            private: this.hasPrivateScope() ? 1 : 0,
            ...this.props.location.query
          }
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

            let newGhRepo = (this.state.ghRepoList || []).find(
              r => r.name === ghRepo.name
            );
            newGhRepo.loading = false;

            throw error;
          });
      }
    );
  };

  hasPrivateScope() {
    const {identities} = this.props;
    const github = identities && identities.find(i => i.provider === 'github');
    return github && github.scopes.indexOf('repo') !== -1;
  }

  renderBody() {
    let {location} = this.props;
    let query = location.query || {};

    const repositories = sortBy(
      this.state.ghRepoList || [],
      repo => `${Number(!repo.active)}:${Number(!repo.admin)}: ${repo.name}}`
    );

    return (
      <Flex>
        <Box flex="1" width={2 / 12} pr={15}>
          <div style={{marginBottom: 10, fontSize: '0.8em'}}>
            {!this.hasPrivateScope() && (
              <Button
                onClick={() =>
                  this.context.router.push({
                    ...location,
                    query: {
                      ...query,
                      private: true
                    }
                  })
                }>
                Enable Private Repos
              </Button>
            )}
          </div>
          <ul>
            <li key="_">
              <Link to={{query: {}, pathname: this.props.location.pathname}}>mine</Link>
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
          <ResultGrid>
            {repositories.map(ghRepo => {
              return (
                <GitHubRepoItem
                  key={ghRepo.name}
                  repo={ghRepo}
                  onEnableRepo={() => this.onToggleRepo(ghRepo.name, true)}
                  onDisableRepo={() => this.onToggleRepo(ghRepo.name, false)}
                />
              );
            })}
          </ResultGrid>
        </Box>
      </Flex>
    );
  }
}

export default connect(
  ({auth}) => ({
    identities: auth.identities
  }),
  {
    addIndicator,
    removeIndicator,
    addRepo,
    removeRepo,
    updateRepo
  }
)(GitHubRepositoryList);
