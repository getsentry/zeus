import React from 'react';
import {Link} from 'react-router';
import {connect} from 'react-redux';
import PropTypes from 'prop-types';
import {Flex, Box} from 'grid-styled';

import AsyncPage from '../components/AsyncPage';
import Button from '../components/Button';
import Panel from '../components/Panel';
import ResultGridHeader from '../components/ResultGridHeader';
import ResultGridRow from '../components/ResultGridRow';
import SectionHeading from '../components/SectionHeading';
import TimeSince from '../components/TimeSince';

import {addIndicator, removeIndicator} from '../actions/indicators';

class RepositoryHooks extends AsyncPage {
  static contextTypes = {
    ...AsyncPage.contextTypes,
    repo: PropTypes.object.isRequired
  };

  getEndpoints() {
    let repo = this.context.repo;
    return [['hookList', `/repos/${repo.full_name}/hooks`]];
  }

  createHook = e => {
    let {repo} = this.context;
    let indicator = this.props.addIndicator('Saving changes..', 'loading');
    this.api
      .post(`/repos/${repo.full_name}/hooks`, {
        data: {
          provider: 'travis'
        }
      })
      .then(hook => {
        this.props.removeIndicator(indicator);
        this.context.router.push(`/${repo.full_name}/settings/hooks/${hook.id}`);
      })
      .catch(error => {
        this.props.addIndicator('An error occurred.', 'error', 5000);
        this.props.removeIndicator(indicator);
        throw error;
      });
  };

  renderBody() {
    let repo = this.context.repo;
    let {hookList} = this.state;
    return (
      <div>
        <div>
          <div style={{float: 'right', marginTop: -5}}>
            <Button onClick={this.createHook} type="primary" size="small">
              Create Hook
            </Button>
          </div>
          <SectionHeading>Hooks</SectionHeading>
        </div>
        <Panel>
          {hookList.length
            ? <div>
                <ResultGridHeader>
                  <Flex>
                    <Box flex="1" width={9 / 12} pr={15}>
                      ID
                    </Box>
                    <Box width={1 / 12} style={{textAlign: 'center'}}>
                      Provider
                    </Box>
                    <Box width={2 / 12} style={{textAlign: 'right'}}>
                      Created
                    </Box>
                  </Flex>
                </ResultGridHeader>
                {hookList.map(hook => {
                  return (
                    <ResultGridRow key={hook.id}>
                      <Flex>
                        <Box flex="1" width={9 / 12} pr={15}>
                          <Link to={`/${repo.full_name}/settings/hooks/${hook.id}`}>
                            {hook.id}
                          </Link>
                        </Box>
                        <Box width={1 / 12} style={{textAlign: 'center'}}>
                          {hook.provider}
                        </Box>
                        <Box width={2 / 12} style={{textAlign: 'right'}}>
                          <TimeSince date={hook.created_at} />
                        </Box>
                      </Flex>
                    </ResultGridRow>
                  );
                })}
              </div>
            : <ResultGridRow>
                {"You haven't registered any hooks for this repository yet."}
              </ResultGridRow>}
        </Panel>
      </div>
    );
  }
}

export default connect(null, {
  addIndicator,
  removeIndicator
})(RepositoryHooks);
