import React, {Component} from 'react';
import PropTypes from 'prop-types';

import api from '../api';
import AsyncPage from '../components/AsyncPage';
import Button from '../components/Button';
import Fieldset from '../components/Fieldset';
import FormActions from '../components/FormActions';
import Input from '../components/Input';
import Label from '../components/Label';
import Panel from '../components/Panel';
import Section from '../components/Section';
import SidebarLayout from '../components/SidebarLayout';

class GitHubProviderOptions extends Component {
  static propTypes = {
    onChange: PropTypes.func.isRequired
  };

  constructor(props, context) {
    super(props, context);
    this.state = {
      formValue: {
        'github.name': ''
      }
    };
  }

  onChangeField = e => {
    this.onChange({
      ...this.state.formValue,
      [e.target.name]: e.target.value
    });
  };

  onChange = formValue => {
    this.setState({formValue});
    this.props.onChange(formValue);
  };

  render() {
    let {formValue} = this.state;
    return (
      <Fieldset>
        <Label>Repository name</Label>
        <Input
          type="text"
          name="github.name"
          value={formValue['github.name']}
          onChange={this.onChangeField}
          placeholder="e.g. getsentry/zeus"
        />
      </Fieldset>
    );
  }
}

class AddRepositoryBody extends Component {
  constructor(props, context) {
    super(props, context);
    this.state = {
      provider: null,
      providerConfig: {}
    };
  }

  renderProviderOptions() {
    switch (this.state.provider) {
      case 'github':
        return <GitHubProviderOptions onChange={this.onChangeProviderOptions} />;
      default:
        return null;
    }
  }

  onChangeProviderOptions = providerConfig => {
    this.setState({providerConfig});
  };

  onSubmit = e => {
    e.preventDefault();
    let {provider, providerConfig} = this.state;
    api
      .post('/repos', {
        data: {
          provider,
          ...providerConfig
        }
      })
      .then(data => {})
      .catch(error => {
        let {data, xhr} = error;
        if (xhr.status === 401) {
          if (data.error == 'identity_needs_upgrade') {
            window.location.href = data.url;
            return;
          }
        }
        throw error;
      });
  };

  render() {
    let providerList = [['github', 'GitHub.com']];
    return (
      <form onSubmit={this.onSubmit}>
        <Label>Add Repository</Label>
        <p>Where is your repository hosted?</p>
        <ul>
          {providerList.map(([pId, pLabel]) => {
            return (
              <li key={pId}>
                <Label key={pId}>
                  <Input
                    type="radio"
                    name="provider"
                    value={pId}
                    checked={this.state.provider === pId}
                    onChange={() => this.setState({provider: pId})}
                  />{' '}
                  {pLabel}
                </Label>
              </li>
            );
          })}
        </ul>
        {this.renderProviderOptions()}
        <FormActions>
          <Button type="submit">Submit</Button>
        </FormActions>
      </form>
    );
  }
}

export default class AddRepository extends AsyncPage {
  getTitle() {
    return 'Add Repository';
  }

  renderBody() {
    return (
      <SidebarLayout title={this.getTitle()}>
        <Section>
          <Panel>
            <AddRepositoryBody {...this.props} />
          </Panel>
        </Section>
      </SidebarLayout>
    );
  }
}
