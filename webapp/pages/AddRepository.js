import React, {Component} from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';

import api from '../api';
import AsyncPage from '../components/AsyncPage';
import {Breadcrumbs, Crumb} from '../components/Breadcrumbs';
import Content from '../components/Content';
import ScrollView from '../components/ScrollView';
import Section from '../components/Section';
import SectionHeading from '../components/SectionHeading';
import Sidebar from '../components/Sidebar';

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
      <fieldset>
        <Label>Repository name</Label>
        <input
          type="text"
          name="github.name"
          value={formValue['github.name']}
          onChange={this.onChangeField}
          placeholder="e.g. getsentry/zeus"
        />
      </fieldset>
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
          if (data.needUpgrade) {
            window.location.href = data.upgradeUrl;
            return;
          }
        }
        throw error;
      });
  };

  render() {
    let providerList = [['github', 'GitHub.com'], ['native', 'Other']];
    return (
      <form onSubmit={this.onSubmit}>
        <SectionHeading>Add Repository</SectionHeading>
        <p>Where is your repository hosted?</p>
        <ul>
          {providerList.map(([pId, pLabel]) => {
            return (
              <li key={pId}>
                <Label key={pId}>
                  <input
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
        <div>
          <button type="submit">Submit</button>
        </div>
      </form>
    );
  }
}

const Label = styled.label`
  margin-bottom: 10px;
  display: block;
`;

export default class AddRepository extends AsyncPage {
  getTitle() {
    return 'Add Repository';
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
              <AddRepositoryBody {...this.props} />
            </Section>
          </ScrollView>
        </Content>
      </div>
    );
  }
}
