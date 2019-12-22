import React from 'react';
import { connect } from 'react-redux';

import AsyncPage from '../components/AsyncPage';
import Label from '../components/Label';
import Section from '../components/Section';
import SectionHeading from '../components/SectionHeading';

import { addIndicator, removeIndicator } from '../actions/indicators';

class RepositorySettings extends AsyncPage {
  getEndpoint() {
    let { provider, ownerName, repoName } = this.props.params;
    return `/repos/${provider}/${ownerName}/${repoName}`;
  }

  getEndpoints() {
    return [['repo', this.getEndpoint()]];
  }

  togglePublic = () => {
    let { repo } = this.state;
    let indicator = this.props.addIndicator('Saving changes..', 'loading');
    this.api
      .put(this.getEndpoint(), {
        data: {
          public: !repo.public
        }
      })
      .then(result => {
        this.props.removeIndicator(indicator);
        this.props.addIndicator('Changes saved!', 'success', 5000);
        this.setState({ repo: result });
      })
      .catch(error => {
        this.props.addIndicator('An error occurred.', 'error', 5000);
        this.props.removeIndicator(indicator);
        throw error;
      });
  };

  renderBody() {
    let { repo } = this.state;
    return (
      <div>
        <SectionHeading>Settings</SectionHeading>
        <Section>
          <Label>
            <input type="checkbox" checked={repo.public} onChange={this.togglePublic} />{' '}
            {'Allow any authenticated user read-only access to this repository in Zeus'}
          </Label>
        </Section>
      </div>
    );
  }
}

export default connect(null, {
  addIndicator,
  removeIndicator
})(RepositorySettings);
