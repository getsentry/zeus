import React from 'react';
import {Link} from 'react-router';
import {connect} from 'react-redux';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import Button from '../components/Button';

import {addIndicator, removeIndicator} from '../actions/indicators';

class RepositoryHooks extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  getEndpoints() {
    let repo = this.context.repo;
    return [['hookList', `/repos/${repo.full_name}/hooks`]];
  }

  createHook = e => {
    let {repo} = this.context;
    let indicator = this.props.addIndicator('Saving changes..', 'loading');
    this.api
      .post(`/repos/${repo.full_name}/hooks`, {
        data: {
          provider: 'travis'
        }
      })
      .then(hook => {
        this.props.removeIndicator(indicator);
        this.context.router.push(`/${repo.full_name}/settings/hooks/${hook.id}`);
      })
      .catch(error => {
        this.props.addIndicator('An error occurred.', 'error', 5000);
        this.props.removeIndicator(indicator);
        throw error;
      });
  };

  renderBody() {
    let repo = this.context.repo;
    let {hookList} = this.state;
    return (
      <div>
        <div>
          <div style={{float: 'right'}}>
            <Button onClick={this.createHook} type="primary">
              Create Hook
            </Button>
          </div>
          <h2>Hooks</h2>
        </div>
        {hookList.length
          ? <ul>
              {hookList.map(hook => {
                return (
                  <li key={hook.id}>
                    <Link to={`/${repo.full_name}/settings/hooks/${hook.id}`}>
                      {hook.id}
                    </Link>
                  </li>
                );
              })}
            </ul>
          : <p>
              {"You haven't registered any hooks for this repository yet."}
            </p>}
      </div>
    );
  }
}

export default connect(null, {
  addIndicator,
  removeIndicator
})(RepositoryHooks);
