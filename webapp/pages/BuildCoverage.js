import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';

import AsyncComponent from '../components/AsyncComponent';

export default class BuildCoverage extends AsyncComponent {
  static contextTypes = {
    ...AsyncComponent.contextTypes,
    build: PropTypes.object.isRequired
  };

  getEndpoints() {
    let {buildNumber, repoName} = this.props.params;
    return [['fileCoverage', `/repos/${repoName}/builds/${buildNumber}/file-coverage`]];
  }

  renderBody() {
    return (
      <Section>
        <List>
          {this.state.fileCoverage.map(coverage => {
            return (
              <ListItem key={coverage.filename}>
                {coverage.filename}
              </ListItem>
            );
          })}
        </List>
      </Section>
    );
  }
}

const Section = styled.div`padding: 30px;`;

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
