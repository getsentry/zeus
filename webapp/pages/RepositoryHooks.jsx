import React from 'react';
import {Link} from 'react-router';
import PropTypes from 'prop-types';

import AsyncPage from '../components/AsyncPage';
import {ButtonLink} from '../components/Button';
import {ResultGrid, Column, Header, Row} from '../components/ResultGrid';
import SectionHeading from '../components/SectionHeading';
import TimeSince from '../components/TimeSince';

export default class RepositoryHooks extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  getEndpoints() {
    let repo = this.context.repo;
    return [['hookList', `/repos/${repo.full_name}/hooks`]];
  }

  renderBody() {
    let repo = this.context.repo;
    let {hookList} = this.state;
    return (
      <div>
        <div>
          <div style={{float: 'right', marginTop: -5}}>
            <ButtonLink
              to={`/${repo.full_name}/settings/hooks/create`}
              type="primary"
              size="small">
              Create Hook
            </ButtonLink>
          </div>
          <SectionHeading>Hooks</SectionHeading>
        </div>
        {hookList.length ? (
          <ResultGrid>
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
          </ResultGrid>
        ) : (
          <div>
            <p>
              Hooks lets you easily upsert build information into Zeus. They&apos;re a set
              of credentials that are bound to this repository.
            </p>
            <p>
              To get started with Zeus, you&apos;ll likely want to{' '}
              <Link to={`/${repo.full_name}/settings/hooks/create`}>
                create a new hook
              </Link>.
            </p>
          </div>
        )}
      </div>
    );
  }
}
