import React from 'react';
import {connect} from 'react-redux';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import Button from '../components/Button';
import SectionHeading from '../components/SectionHeading';

import {addIndicator, removeIndicator} from '../actions/indicators';

export class RepositoryHookCreate extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  createHook = provider => {
    let {repo} = this.context;
    let indicator = this.props.addIndicator('Saving changes..', 'loading');

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
    return (
      <div>
        <div>
          <SectionHeading>Create Hook</SectionHeading>
        </div>
        <p>
          Hooks lets you easily upsert build information into Zeus. They&apos;re a set of
          credentials that are bound to this repository. Once you&apos;ve created the
          hook, it can be used to submit build and job information, as well as to upload
          artifacts (for example, via{' '}
          <a href="https://github.com/getsentry/zeus-cli">zeus-cli</a>
          ).
        </p>
        <p>To create a new hook, select a provider:</p>
        <p>
          <Button onClick={this.createHook.bind(this, 'travis')}>Travis CI</Button>{' '}
          <Button onClick={this.createHook.bind(this, 'custom')}>Custom</Button>
        </p>
      </div>
    );
  }
}

export default connect(
  null,
  {
    addIndicator,
    removeIndicator
  }
)(RepositoryHookCreate);
