import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import {Flex, Box} from 'grid-styled';

import AsyncPage from '../components/AsyncPage';
import Panel from '../components/Panel';
import ResultGridRow from '../components/ResultGridRow';
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
install:
  - npm install zeus-cli
after_success:
  - zeus-cli upload-artifacts --discover
after_failure:
  - zeus-cli upload-artifacts --discover`;
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
        <Panel>
          <ResultGridRow>
            <Flex>
              <Box flex="1" width={1 / 12} pr={15}>
                <strong>ID</strong>
              </Box>
              <Box width={10 / 12}>
                {hook.id}
              </Box>
            </Flex>
          </ResultGridRow>
          <ResultGridRow>
            <Flex>
              <Box flex="1" width={1 / 12} pr={15}>
                <strong>Provider</strong>
              </Box>
              <Box width={10 / 12}>
                {hook.provider}
              </Box>
            </Flex>
          </ResultGridRow>
          <ResultGridRow>
            <Flex>
              <Box flex="1" width={1 / 12} pr={15}>
                <strong>Token</strong>
              </Box>
              <Box width={10 / 12}>
                {hook.token
                  ? <code>
                      {hook.token}
                    </code>
                  : <em>hidden</em>}
              </Box>
            </Flex>
          </ResultGridRow>
          <ResultGridRow>
            <Flex>
              <Box flex="1" width={1 / 12} pr={15}>
                <strong>Created</strong>
              </Box>
              <Box width={10 / 12}>
                <TimeSince date={hook.created_at} />
              </Box>
            </Flex>
          </ResultGridRow>
        </Panel>

        <SectionHeading>Travis Config</SectionHeading>
        <Panel>
          <Config>
            {generateTravisConfig(publicHookBase)}
          </Config>
        </Panel>
      </div>
    );
  }
}

const Config = styled.pre`
  padding: 0 20px;
  font-size: 13px;
`;
