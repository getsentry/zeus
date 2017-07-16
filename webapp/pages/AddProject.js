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
import Select from '../components/Select';
import SidebarLayout from '../components/SidebarLayout';

class AddProjectBody extends Component {
  static contextTypes = {
    orgList: PropTypes.arrayOf(PropTypes.object).isRequired
  };

  constructor(props, context) {
    super(props, context);
    this.state = {
      formValue: {
        name: ''
      },
      selectedOrg: context.orgList.find(_ => true).name
    };
  }

  onChange = formValue => {
    this.setState({formValue});
  };

  onChangeField = e => {
    this.onChange({
      ...this.state.formValue,
      [e.target.name]: e.target.value
    });
  };

  onChangeSelectField = e => {
    this.setState({
      ...this.state.formValue,
      [e.target.name]: e.target.options[e.target.selectedIndex]
    });
  };

  onChangeOrg = e => {
    this.setState({
      selectedOrg: e.target.options[e.target.selectedIndex]
    });
  };

  onSubmit = e => {
    e.preventDefault();
    let {formValue, selectedOrg} = this.state;
    api
      .post(`/organizations/${selectedOrg}/projects`, {
        data: formValue
      })
      .then(data => {});
  };

  render() {
    let {formValue, selectedOrg} = this.state;
    return (
      <form onSubmit={this.onSubmit}>
        <Fieldset>
          <Label>Organization</Label>
          <Select
            name="organization"
            onChange={this.onChangeOrg}
            required={true}
            value={selectedOrg}>
            {this.context.orgList.map(o => {
              return (
                <option key={o.name}>
                  {o.name}
                </option>
              );
            })}
          </Select>
        </Fieldset>
        <Fieldset>
          <Label>Project name</Label>
          <Input
            type="text"
            name="name"
            value={formValue.name}
            onChange={this.onChangeField}
            placeholder="e.g. zeus"
            required={true}
          />
        </Fieldset>
        <Fieldset>
          <Label>Repository</Label>
          <Select
            name="repository"
            onChange={this.onChangeSelectField}
            required={true}
            value={formValue.repository}>
            {[].map(o => {
              return (
                <option key={o.id}>
                  {o.url}
                </option>
              );
            })}
          </Select>
        </Fieldset>
        <FormActions>
          <Button type="submit">Submit</Button>
        </FormActions>
      </form>
    );
  }
}

export default class AddProject extends AsyncPage {
  getTitle() {
    return 'Add Project';
  }

  renderBody() {
    return (
      <SidebarLayout title={this.getTitle()}>
        <Section>
          <Panel>
            <AddProjectBody {...this.props} />
          </Panel>
        </Section>
      </SidebarLayout>
    );
  }
}
