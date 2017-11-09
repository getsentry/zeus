import React from 'react';
import {Link} from 'react-router';
import {connect} from 'react-redux';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import Button from '../components/Button';
import {ResultGrid, Column, Header, Row} from '../components/ResultGrid';
import SectionHeading from '../components/SectionHeading';
import TimeSince from '../components/TimeSince';

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

    // eslint-disable-next-line
    const provider = window.prompt('Please enter a service name', 'travis');
    if (!provider) return;

    this.api
      .post(`/repos/${repo.full_name}/hooks`, {
        data: {provider}
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
          <div style={{float: 'right', marginTop: -5}}>
            <Button onClick={this.createHook} type="primary" size="small">
              Create Hook
            </Button>
          </div>
          <SectionHeading>Hooks</SectionHeading>
        </div>
        <ResultGrid>
          {hookList.length ? (
            <div>
              <Header>
                <Column>ID</Column>
                <Column width={120}>Provider</Column>
                <Column width={150}>Created</Column>
              </Header>
              {hookList.map(hook => {
                return (
                  <Row key={hook.id}>
                    <Column>
                      <Link to={`/${repo.full_name}/settings/hooks/${hook.id}`}>
                        {hook.id}
                      </Link>
                    </Column>
                    <Column width={120}>{hook.provider}</Column>
                    <Column width={150}>
                      <TimeSince date={hook.created_at} />
                    </Column>
                  </Row>
                );
              })}
            </div>
          ) : (
            <Row>
              <Column>
                {"You haven't registered any hooks for this repository yet."}
              </Column>
            </Row>
          )}
        </ResultGrid>
      </div>
    );
  }
}

export default connect(null, {
  addIndicator,
  removeIndicator
})(RepositoryHooks);
