import React from 'react';
import PropTypes from 'prop-types';
import styled from '@emotion/styled';
import Select from 'react-select';

import AsyncPage from '../components/AsyncPage';
import Panel from '../components/Panel';
import {ResultGrid, Column, Row} from '../components/ResultGrid';
import SectionHeading from '../components/SectionHeading';
import TimeSince from '../components/TimeSince';

const TRAVIS_DOMAIN_OPTIONS = [
  {value: 'api.travis-ci.org', label: 'travis-ci.org'},
  {value: 'api.travis-ci.com', label: 'travis-ci.com'}
];

const generateTravisConfig = publicHookBase => {
  return `notifications:
  webhooks:
    urls:
      - ${publicHookBase}/provider/travis/webhook
    on_success: always
    on_failure: always
    on_start: always
    on_cancel: always
    on_error: always
after_script:
  - npm install -g @zeus-ci/cli
  - zeus upload -t "mime/type" path/to/artifact`;
};

export default class RepositoryHookDetails extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  getEndpoints() {
    let {params} = this.props;
    return [['hook', `/hooks/${params.hookId}`]];
  }

  getHookBase(secret = false) {
    let {hook} = this.state;
    let {hostname, port, protocol} = document.location;

    if (protocol === 'http') port = port === 80 ? '' : `:${port}`;
    else if (protocol === 'http') port = port === 443 ? '' : `:${port}`;

    return `${protocol}//${hostname}${port}${secret ? hook.secret_uri : hook.public_uri}`;
  }

  onChangeIsRequired = e => {
    let {params} = this.props;

    let data = {
      is_required: e.target.checked
    };

    this.api.put(`/hooks/${params.hookId}`, {data});
  };

  onChangeConfig = (key, value) => {
    let {hook} = this.state;
    let {params} = this.props;

    let data = {
      config: {
        ...hook.config,
        [key]: value
      }
    };

    this.api.put(
      `/hooks/${params.hookId}`,
      {data},
      this.setState({
        hook: {
          ...hook,
          ...data
        }
      })
    );
  };

  renderBody() {
    let {hook} = this.state;
    let publicHookBase = this.getHookBase(false);
    return (
      <div>
        <h2>Hook Details</h2>
        <ResultGrid>
          <Row>
            <Column width={200}>
              <strong>ID</strong>
            </Column>
            <Column textAlign="left">{hook.id}</Column>
          </Row>
          <Row>
            <Column width={200}>
              <strong>Provider</strong>
            </Column>
            <Column textAlign="left">{hook.provider}</Column>
          </Row>
          <Row>
            <Column width={200}>
              <strong>Token</strong>
            </Column>
            <Column textAlign="left">
              {hook.token ? <code>{hook.token}</code> : <em>hidden</em>}
            </Column>
          </Row>
          <Row>
            <Column width={200}>
              <strong>ZEUS_HOOK_BASE</strong>
            </Column>
            <Column textAlign="left">
              <code>{this.getHookBase(true)}</code>
            </Column>
          </Row>
          <Row>
            <Column width={200}>
              <strong>Required?</strong>
            </Column>
            <Column textAlign="left">
              <input
                type="checkbox"
                checked={hook.is_required}
                onChange={this.onChangeIsRequired}
              />
            </Column>
          </Row>
          <Row>
            <Column width={200}>
              <strong>Created</strong>
            </Column>
            <Column textAlign="left">
              <TimeSince date={hook.created_at} />
            </Column>
          </Row>
          {hook.provider.startsWith('travis') && (
            <Row>
              <Column width={200}>
                <strong>Domain</strong>
              </Column>
              <OverflowColumn textAlign="left">
                <Select
                  placeholder=""
                  clearable={false}
                  options={TRAVIS_DOMAIN_OPTIONS}
                  onChange={({value}) => this.onChangeConfig('domain', value)}
                  value={hook.config.domain || TRAVIS_DOMAIN_OPTIONS[0]}
                />
              </OverflowColumn>
            </Row>
          )}
          {hook.provider === 'custom' && (
            <Row>
              <Column width={200}>
                <strong>Service Name</strong>
              </Column>
              <OverflowColumn textAlign="left">
                <div style={{marginBottom: 5}}>
                  <input
                    type="text"
                    placeholder=""
                    onChange={e => this.onChangeConfig('name', e.target.value)}
                    value={hook.config.name || 'custom'}
                  />
                </div>
                <div style={{fontSize: '90%'}}>
                  Enter a service name unique to this provider. It will be captured and
                  keyed with each reported build.
                </div>
              </OverflowColumn>
            </Row>
          )}
        </ResultGrid>

        {hook.provider.startsWith('travis') && (
          <div>
            <SectionHeading>Travis Config</SectionHeading>
            <Panel>
              <Config>{generateTravisConfig(publicHookBase)}</Config>
            </Panel>
          </div>
        )}
      </div>
    );
  }
}

const OverflowColumn = styled(Column)`
  overflow: visible;
`;

const Config = styled.pre`
  padding: 0 20px;
  font-size: 13px;
`;
