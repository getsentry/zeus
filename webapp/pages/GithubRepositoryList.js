import React from 'react';
import {Flex, Box} from 'grid-styled';

import AsyncPage from '../components/AsyncPage';
import Panel from '../components/Panel';
import ResultGridHeader from '../components/ResultGridHeader';
import ResultGridRow from '../components/ResultGridRow';
import Section from '../components/Section';
import SectionHeading from '../components/SectionHeading';
import SidebarWrapper from '../components/SidebarWrapper';

export default class GitHubRepositoryList extends AsyncPage {
  getTitle() {
    return 'Repositories';
  }

  renderBody() {
    return (
      <SidebarWrapper title={this.getTitle()}>
        <GitHubRepositoryListBody {...this.props} />
      </SidebarWrapper>
    );
  }
}

class GitHubRepositoryListBody extends AsyncPage {
  getEndpoints() {
    return [['ghRepoList', `/github/repos`]];
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
          {this.state.ghRepoList.map(repo => {
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
