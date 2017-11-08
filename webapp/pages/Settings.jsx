import React from 'react';
import PropTypes from 'prop-types';
import {Link} from 'react-router';

import AsyncPage from '../components/AsyncPage';
import Button from '../components/Button';
import Layout from '../components/Layout';
import {ResultGrid, Column, Row} from '../components/ResultGrid';
import SectionHeading from '../components/SectionHeading';

export default class Settings extends AsyncPage {
  static contextTypes = {
    repoList: PropTypes.arrayOf(PropTypes.object).isRequired,
    router: PropTypes.object.isRequired
  };

  getTitle() {
    return 'Settings';
  }

  render() {
    return (
      <Layout title={this.getTitle()}>
        {this.renderContent()}
      </Layout>
    );
  }

  renderBody() {
    return (
      <div>
        <h1>
          {"These are your settings. There's not much to them yet."}
        </h1>

        <div>
          <div style={{float: 'right', marginTop: -5}}>
            <Button
              onClick={() => {
                this.context.router.push('/settings/github/repos');
              }}
              type="primary"
              size="small">
              Manage GitHub Repositories
            </Button>
          </div>
          <SectionHeading>Repositories</SectionHeading>
        </div>
        <ResultGrid>
          {this.context.repoList.map(repo => {
            return (
              <Row key={repo.id}>
                <Column>
                  <Link to={repo.full_name}>
                    {repo.owner_name} / {repo.name}
                  </Link>
                </Column>
              </Row>
            );
          })}
        </ResultGrid>
      </div>
    );
  }
}
