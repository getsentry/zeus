import React from 'react';
import styled from 'styled-components';

import AsyncComponent from '../components/AsyncComponent';
import Duration from '../components/Duration';
import Section from '../components/Section';

export default class BuildTestList extends AsyncComponent {
  getEndpoints() {
    let {buildNumber, repoName} = this.props.params;
    return [['testList', `/repos/${repoName}/builds/${buildNumber}/tests`]];
  }

  renderBody() {
    return (
      <Section>
        <List>
          {this.state.testList.map(test => {
            return (
              <ListItem key={test.id}>
                {test.name} &mdash; <Duration ms={test.duration} short={true} />
              </ListItem>
            );
          })}
        </List>
      </Section>
    );
  }
}

const List = styled.div`
  border: 1px solid #d8d7e0;
  border-radius: 4px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, .06);
`;

const ListItem = styled.div`
  border-top: 1px solid #e0e4e8;
  display: flex;
  align-items: center;
  padding: 10px 15px;

  &:first-child {
    border: 0;
  }
`;
