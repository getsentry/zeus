import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';

import AsyncPage from '../components/AsyncPage';
import Panel from '../components/Panel';
import {ResultGrid, Column, Row} from '../components/ResultGrid';
import SectionHeading from '../components/SectionHeading';
import TimeSince from '../components/TimeSince';

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
  email: false
install:
  - npm install zeus-ci
after_success:
  - zeus-ci upload path/to/artifact "mime/type"
after_failure:
  - zeus-ci upload path/to/artifact "mime/type"`;
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
            <Column textAlign="left">
              {hook.id}
            </Column>
          </Row>
          <Row>
            <Column width={200}>
              <strong>Provider</strong>
            </Column>
            <Column textAlign="left">
              {hook.provider}
            </Column>
          </Row>
          <Row>
            <Column width={200}>
              <strong>Token</strong>
            </Column>
            <Column textAlign="left">
              {hook.token
                ? <code>
                    {hook.token}
                  </code>
                : <em>hidden</em>}
            </Column>
          </Row>
          <Row>
            <Column width={200}>
              <strong>ZEUS_HOOK_BASE</strong>
            </Column>
            <Column textAlign="left">
              <code>
                {this.getHookBase(true)}
              </code>
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
        </ResultGrid>

        {hook.provider.startsWith('travis') &&
          <div>
            <SectionHeading>Travis Config</SectionHeading>
            <Panel>
              <Config>
                {generateTravisConfig(publicHookBase)}
              </Config>
            </Panel>
          </div>}
      </div>
    );
  }
}

const Config = styled.pre`
  padding: 0 20px;
  font-size: 13px;
`;
