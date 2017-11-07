import React from 'react';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';

export default class RepositoryHookDetails extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  getEndpoints() {
    let {params} = this.props;
    return [['hook', `/hooks/${params.hookId}`]];
  }

  getHookBase() {
    let {hook} = this.state;
    let {hostname, port, protocol} = document.location;

    if (protocol === 'http') port = port === 80 ? '' : `:${port}`;
    else if (protocol === 'http') port = port === 443 ? '' : `:${port}`;

    return `${protocol}//${hostname}${port}${hook.base_uri}`;
  }

  renderBody() {
    let {hook} = this.state;
    let hookBase = this.getHookBase();
    // let repo = this.context.repo;
    // let basePath = `/${repo.full_name}`;
    return (
      <div>
        <h2>
          Hook <small>{hook.id}</small>
        </h2>
        <dl className="flat">
          <dt>Provider:</dt>
          <dd>
            {hook.provider}
          </dd>
          <dt>Token:</dt>
          <dd>
            {hook.token
              ? <code>
                  {hook.token}
                </code>
              : <em>hidden</em>}
          </dd>
          <dt>Base Path:</dt>
          <dd>
            <code>
              {hookBase}
            </code>
          </dd>
        </dl>

        <h3>Travis Config</h3>
        <h4>Environment</h4>
        <pre>
          ZEUS_HOOK_BASE={hookBase}
        </pre>
        <h4>Webhooks</h4>
        <pre>
          {`notifications:\n  webhooks:\n    urls:\n      - ${hookBase}/provider/travis/webhook\n    on_start: always`}
        </pre>
      </div>
    );
  }
}
