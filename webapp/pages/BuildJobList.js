import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';

import AsyncComponent from '../components/AsyncComponent';
import Section from '../components/Section';

export default class BuildJobList extends AsyncComponent {
  static contextTypes = {
    ...AsyncComponent.contextTypes,
    build: PropTypes.object.isRequired
  };

  getEndpoints() {
    let {buildNumber, repoName} = this.props.params;
    return [['jobList', `/repos/${repoName}/builds/${buildNumber}/jobs`]];
  }

  renderBody() {
    let {build} = this.context;
    return (
      <Section>
        <List>
          {this.state.jobList.map(job => {
            return (
              <ListItem key={job.id}>
                #{build.number}.{job.number} &mdash; {job.id}
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
