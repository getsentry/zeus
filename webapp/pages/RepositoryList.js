import React from 'react';
import {Flex, Box} from 'grid-styled';

import AsyncPage from '../components/AsyncPage';
import {Breadcrumbs, Crumb} from '../components/Breadcrumbs';
import Panel from '../components/Panel';
import ResultGridHeader from '../components/ResultGridHeader';
import ResultGridRow from '../components/ResultGridRow';
import Section from '../components/Section';
import SectionHeading from '../components/SectionHeading';
import ScrollView from '../components/ScrollView';

export default class RepositoryList extends AsyncPage {
  getTitle() {
    return 'Repositories';
  }

  renderBody() {
    let {params} = this.props;
    return (
      <div>
        <Breadcrumbs>
          <Crumb active={true}>
            {params.orgName}
          </Crumb>
        </Breadcrumbs>
        <ScrollView>
          <RepositoryListBody {...this.props} />
        </ScrollView>
      </div>
    );
  }
}

class RepositoryListBody extends AsyncPage {
  getEndpoints() {
    let {orgName} = this.props.params;
    return [['repoList', `/organizations/${orgName}/repos`]];
  }

  renderBody() {
    return (
      <Section>
        <SectionHeading>Repositories</SectionHeading>
        <Panel>
          <ResultGridHeader>
            <Flex>
              <Box flex="1" width={10 / 12} pr={15}>
                Repository
              </Box>
              <Box width={2 / 12} style={{textAlign: 'center'}}>
                Provider
              </Box>
            </Flex>
          </ResultGridHeader>
          {this.state.repoList.map(repo => {
            return (
              <ResultGridRow key={repo.id}>
                <Flex>
                  <Box flex="1" width={10 / 12} pr={15}>
                    {repo.url}
                  </Box>
                  <Box width={2 / 12} style={{textAlign: 'center'}}>
                    {repo.provider}
                  </Box>
                </Flex>
              </ResultGridRow>
            );
          })}
        </Panel>
      </Section>
    );
  }
}
